from flask import (
    Flask, 
    render_template, 
    redirect, abort, 
    request)
from flask_login import (
    LoginManager, 
    login_user, 
    logout_user, 
    login_required, 
    current_user)
from datetime import datetime, timedelta
import pandas as pd
import json
import plotly
import plotly.express as px

from data import db_session
from data.users import User
from data.records import Records
from data.act_names import Activities_names

from forms.users import RegisterForm
from forms.login import LoginForm
from forms.record import RecordForm
from forms.activity import ActivityForm
from forms.sum_report import ReportSumForm

from config import *
from functional_counting import Date_picker


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)


def get_remaining_time_handler(lst):
    ans = []
    for item in lst:
        dt = item.created_date
        remain = Date_picker.get_time(dt, datetime.now())
        act_name = item.act_n.name
        work_time = f'{act_name} - затрачено {item.work_hours + item.work_min // 30} ч.'
        ans.append((item.id, remain, work_time))
    return ans


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/",  methods=['GET', 'POST'])
def index():
    params = {'title': 'Домашняя страница',
              'description1': 'Домашняя страница',
              'description2': 'Сначала войдите в аккаунт или заведите новый.',
              'status_page': 0}
    if current_user.is_authenticated:
        params['description2'] = 'Тут можно записать время на активности и посмотреть простую статистику.'
        db_sess = db_session.create_session()

        form = RecordForm()
        params['form'] = form
        activities = db_sess.query(Activities_names).filter(
            Activities_names.user == current_user).all()
        params['activities'] = activities

        form.activity.choices = [(item.id, item.name) for item in activities]
        recs = db_sess.query(Records).filter(
            Records.user == current_user).order_by(Records.id).all()[-3:]
        records_on_site = get_remaining_time_handler(recs)
        params['records_list'] = records_on_site


        # print(form.date.data, form.activity.data, form.work_hour.data, form.work_min.data, form.validate_on_submit())
        if form.validate_on_submit():
            if form.work_hour.data < 0 or form.work_min.data < 0 or (form.work_hour.data == form.work_min.data == 0):
                return render_template("index.html", error="Некорректное значение времени", **params)

            record = Records()
            record.name_id = form.activity.data
            record.created_date = datetime.now() if form.date.data == datetime.now().date() else form.date.data
            record.work_hours = form.work_hour.data
            record.work_min = form.work_min.data
            current_user.records.append(record)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        # else: print(form.date.data, form.activity.data, form.work_hour.data, form.work_min.data)
    return render_template("index.html", error="", **params)

@app.route('/cancel/<item_id>')
def cancel(item_id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        db_sess.query(Records).filter(Records.id == item_id).delete()
        db_sess.commit()
    return redirect('/')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    params = {'status_page': 1,
              'title': 'Настройки',
              'error': ""}
    if current_user.is_authenticated:
        activity_form = ActivityForm()
        params['activity_form'] = activity_form
        # print( activity_form.color.data,  activity_form.name.data, activity_form.validate_on_submit(), activity_form.errors)
        if activity_form.validate_on_submit():
            db_sess = db_session.create_session()
            activities = Activities_names(name=activity_form.name.data)
            current_user.act_names.append(activities)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/settings')

    return render_template("settings.html", **params)


"""@app.route("/settings")
def add_act():
    db_sess = db_session.create_session()
    names = ["CCC"]
    acts = Activities_names()
    acts.name = names[i]
    acts.user_id = 1
    current_user.act_names.append(acts)
    db_sess.merge(current_user)
    db_sess.commit()
    return {[item.name for item in db_sess.query(Activities_names).filter(Activities_names.user == current_user)]}"""

@app.route('/reports_summary', methods=['GET', 'POST'])
def bar_with_plotly():
    params = {'title': 'Суммарный отчет',
              'description1': 'Суммарный отчет',
              'description2': 'Сначала войдите в аккаунт или заведите новый.',
              'error': '',
              'status_page': 2}
    if current_user.is_authenticated:
        params['description2'] = 'Тут можно посмотреть чёткую статистику по суммарно проведенному времени.'

        form = ReportSumForm()
        db_sess = db_session.create_session()

        acts = db_sess.query(Activities_names).filter(Activities_names.user == current_user).all()
        lst_ch = [(str(item.id), item.name) for item in acts]
        form.activities.choices = lst_ch
        form.activities.default = lst_ch

        params['form'] = form
        print(form.submit.data, form.to_default.data)
        to_default = False
        if form.to_default.data: to_default = True
        if form.validate_on_submit() and not to_default:
            td = timedelta(1)
            from_date = form.from_date.data if form.from_date.data else datetime.min
            to_date = form.to_date.data + td if form.to_date.data else datetime.now() + td
            acts_id = [int(x) for x in form.activities.data]

            recs = db_sess.query(Records).filter(
                Records.user == current_user,
                from_date <= Records.created_date, 
                Records.created_date < to_date,
                Records.name_id.in_(acts_id)).all()

            activities = [[item.act_n.name, item.work_hours + item.work_min / 60, 'None'] for item in recs]
        else:
            # print(form.errors)
            recs = db_sess.query(Records).filter(Records.user == current_user).all()
            activities = [[item.act_n.name, item.work_hours + item.work_min / 60, 'None'] for item in recs]
            """activities = [['Прога', 34, 'Sydney'],
                        ['Да', 30, 'Coimbatore'],
                        ['Нет', 31, 'Coimbatore'],
                        ['СИНТИПОП', 32, 'Tokyo'],
                        ['Да', 16, 'New York'],
                        ['Спорт', 17, 'Toronto']]"""
            
            # Convert list to dataframe and assign column values
        df = pd.DataFrame(activities,
                        columns=['Активность', 'Часы', 'Группа'])
        
        # Create Bar chart
        fig = px.bar(df, x='Часы', y='Активность', color='Активность', barmode='group', orientation='h')
        
        # Create graphJSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
            # Use render_template to pass graphJSON to html
        return render_template("reports_sum.html", graphJSON=graphJSON, **params)
    return render_template("reports_sum.html", **params)


"""@app.route('/job',  methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        jobs = Jobs()
        f1 = form.work_size.data <= 0
        f2 = form.team_leader.data <= 0
        f3 = not all([x.isnumeric() for x in form.collaborators.data.split(", ")])
        if f1 or f2 or f3:
            return render_template('job.html', title='Добавление работы', form=form)
        db_sess = db_session.create_session()
        jobs.job = form.job.data
        jobs.team_leader = form.team_leader.data
        jobs.work_size = form.work_size.data
        jobs.collaborators = form.collaborators.data
        jobs.is_finished = form.is_finished.data
        db_sess.add(jobs)
        db_sess.commit()
        return redirect('/')
    return render_template('job.html', title='Добавление работы', 
                           form=form)"""


"""@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )"""


"""@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости', 
                           form=form)"""


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data, login=form.login.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("C:/Dev/Olymps/yandex_lyceum/Project3/db/time_mngr_data.db")
    app.run()



if __name__ == '__main__':
    main()