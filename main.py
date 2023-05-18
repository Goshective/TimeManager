from flask import (
    Flask, 
    render_template, 
    redirect, 
    request, 
    make_response,
    abort)
from flask_login import (
    LoginManager, 
    login_user, 
    logout_user, 
    login_required, 
    current_user)
from sqlalchemy.sql import text

from flask_restful import Api
from datetime import datetime, timedelta
import pandas as pd
import json
import plotly
import plotly.express as px
from math import ceil

from data import db_session
from data.users import User
from data.records import Records
from data.act_names import Activities_names
from data.pictures import Pictures

from forms.users import RegisterForm
from forms.login import LoginForm
from forms.record import RecordForm
from forms.activity_add import ActivityAddForm
from forms.activity_change import ActivityChangeForm
from forms.activity_delete import ActivityDeleteForm
from forms.photo_form import PhotoForm
from forms.sum_report import ReportChartForm
from forms.token import TokenForm

from data.api_records import RecordsListResource, RecordsResource

from config import SECRET_KEY
from utilities import (
    get_work_time, get_token, 
    get_pages, get_page_after_delete, 
    db_datetime_formating, get_remaining_time_title)
from form_parser import (add_activity, change_activity, 
                         delete_activity, add_photo,
                         delete_record, add_record)


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
api = Api(app)

api.add_resource(RecordsListResource, '/api/records')
api.add_resource(RecordsResource, '/api/records/<int:record_id>')

login_manager = LoginManager()
login_manager.init_app(app)

HORIZONTAL_BAR = 0
MULTI_BAR = 1
N_SYMBOLS = 40

def get_chart_records(chart_type, params):
    if chart_type == HORIZONTAL_BAR:
        params['description2'] = 'Тут можно посмотреть чёткую статистику по суммарно проведённому времени.'
    else:
        params['description2'] = 'Тут можно посмотреть отчёт о проведённом времени за каждый день.'

    form = ReportChartForm()
    db_sess = db_session.create_session()

    acts = db_sess.query(Activities_names).filter(Activities_names.user == current_user).all()
    lst_ch = [(str(item.id), item.name) for item in acts]
    form.activities.choices = lst_ch

    params['form'] = form

    to_default = False
    if form.to_default.data: to_default = True
    if form.validate_on_submit() and not to_default:
        td = timedelta(1)
        from_date = form.from_date.data if form.from_date.data else datetime.min
        to_date = form.to_date.data + td if form.to_date.data else datetime.now() + td
        acts_id = [int(x) for x in form.activities.data]

        if chart_type == HORIZONTAL_BAR:
            recs = db_sess.query(Records).filter(
                Records.user == current_user,
                from_date <= Records.created_date, 
                Records.created_date < to_date,
                Records.name_id.in_(acts_id)).all()
        else:
            recs = db_sess.query(Records).filter(
                Records.user == current_user,
                from_date <= Records.created_date, 
                Records.created_date < to_date,
                Records.name_id.in_(acts_id)).order_by(
                Records.created_date).all()
    else:
        if chart_type == HORIZONTAL_BAR:
            recs = db_sess.query(Records).filter(
                Records.user == current_user).all()
        else:
            recs = db_sess.query(Records).filter(
                Records.user == current_user).order_by(
                Records.created_date).all()
    return recs, params, db_sess

def get_home_page_statistics():
    with db_session.create_session() as db_sess:
        statement1 = text('''
        SELECT activities_names.name, records.work_hours, records.work_min, records.created_date, records.id
        FROM records
        INNER JOIN activities_names ON records.name_id=activities_names.id
        WHERE records.user_id == :id ORDER BY records.id DESC LIMIT 3''')
        statement2 = text('''
        SELECT COUNT(*), SUM(work_hours), SUM(work_min) FROM records
        WHERE user_id == :id''')
        statement3 = text('''
            SELECT  SUM(work_hours), SUM(work_min) FROM records
            WHERE user_id == :id AND created_date >= :ts''')
        
        last_recs = []
        par = {'id': current_user.id, 'ts': datetime.now() - timedelta(7)}
        par2 = {'id': current_user.id}

        for row in db_sess.execute(statement1, par2):
            dct = {'id': row[4],
                   'name': row[0],
                   'work_hours': row[1],
                   'work_min': row[2], 
                   'created_date': db_datetime_formating(row[3])}
            last_recs.append(dct)
        for row in db_sess.execute(statement3, params=par):
            week_h, week_m = row
        if week_h or week_m:
            week_time = (str(week_h + week_m // 60), str(week_m % 60))
        else:
            week_time = 0, 0

        for row in db_sess.execute(statement2, params=par2):
            n_records, rec_h, rec_m = row
        if n_records or rec_h or rec_m:
            all_time = (str(rec_h + rec_m // 60), str(rec_m % 60))
            av_minute_time = (rec_h * 60 + rec_m) // n_records if n_records != 0 else 0
            average_time = (str(av_minute_time // 60), str(av_minute_time % 60))
        else:
            all_time, average_time = (0, 0), (0, 0)


    return last_recs, week_time, all_time, average_time


@login_manager.user_loader
def load_user(user_id):
    with db_session.create_session() as db_sess:
        return db_sess.query(User).get(user_id)

@app.route("/",  methods=['GET', 'POST'])
def index():
    params = {'title': 'Домашняя страница',
              'description1': 'Домашняя страница',
              'description2': 'Сначала войдите в аккаунт или заведите новый.',
              'error': '',
              'status_page': 0}
    if not current_user.is_authenticated:
        return render_template("index.html", **params)

    db_sess = db_session.create_session()
    db_sess.add(current_user)

    params['description2'] = 'Тут можно записать время на активности и посмотреть простую статистику.'

    form = RecordForm()
    activities = db_sess.query(Activities_names).filter(
            Activities_names.user == current_user).all()
    form.activity.choices = [(item.id, item.name) for item in activities]
    
    if request.method == 'POST':
        code, ans = add_record(form, current_user)
        db_sess.commit()
        if code != 0:
            params['error'] = ans

    last_recs, week_time, all_time, average_time = get_home_page_statistics()
    params['activities'] = activities
    params['week_time'] = week_time
    params['all_time'] = all_time
    params['average_time'] = average_time
    
    records_on_site = get_remaining_time_title(last_recs)
    params['records_list'] = records_on_site
    params['form'] = form
    return render_template("index.html", **params)

@app.route('/cancel/<int:item_id>', methods=['POST'])
def cancel(item_id):
    delete_record(item_id, current_user)
    return redirect('/')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    params = {'status_page': 1,
              'title': 'Настройки',
              'description1': 'Настройки',
              'description2': 'Сначала войдите в аккаунт или заведите новый.'}
    if not current_user.is_authenticated:
        return render_template("settings.html", **params)

    activity_form_add = ActivityAddForm()
    params['activity_form_add'] = activity_form_add

    activity_form_change = ActivityChangeForm()
    with db_session.create_session() as db_sess:
        acts = db_sess.query(Activities_names).filter(Activities_names.user == current_user).all()
        choices = [(str(item.id), item.name) for item in acts]
    activity_form_change.choose_names.choices = choices
    params['activity_form_change'] = activity_form_change

    activity_form_delete = ActivityDeleteForm()
    activity_form_delete.choose_names.choices = choices
    params['activity_form_delete'] = activity_form_delete

    photo_form = PhotoForm()
    params['photo_form'] = photo_form

    if 'submit' in request.form and request.method == 'POST':
        name = request.form['submit']
        if name == 'Загрузить':
            code, ans = add_photo(photo_form, current_user)
            if code == 0: return ans
            params['error_photo'] = ans

        elif name == 'Добавить':
            code, ans = add_activity(activity_form_add, current_user)
            if code == 0: return ans
            params['error_add_form'] = ans

        elif name == 'Изменить':
            code, ans = change_activity(activity_form_change, current_user)
            if code == 0: return ans
            params['error_change_form'] = ans

        elif name == 'Удалить':
            code, ans = delete_activity(activity_form_delete, current_user)
            if code == 0: return ans
            params['error_delete_form'] = ans
    
    return render_template("settings.html", **params)

@app.route('/records_list')
def base_checking_records():
    return redirect('/records_list/1')

@app.route('/records_list/<int:page>', methods=['GET', 'POST'])
def checking_records(page):
    if page < 1: return abort(404)
    params = {'title': 'Записи',
              'description1': 'Записи',
              'description2': 'Сначала войдите в аккаунт или заведите новый.',
              'error': '',
              'status_page': 5}
    if not current_user.is_authenticated:
        return render_template("settings.html", **params)

    amount_records_page = 10
    skip_records = (page - 1) * amount_records_page

    params['description2'] = 'Отображены на страницах'
    with db_session.create_session() as db_sess:
        statement = text('''
        SELECT activities_names.name, records.work_hours, 
        records.work_min, records.created_date, records.id
        FROM records
        INNER JOIN activities_names ON records.name_id=activities_names.id
        WHERE records.user_id == :id ORDER BY records.id
        DESC LIMIT :skip_records, :amount_recs_page''')
        statement_count = text('''
        SELECT COUNT(*) FROM RECORDS WHERE user_id == :id''')
        
        page_recs = []
        par = {'id': current_user.id, 'amount_recs_page': amount_records_page, 'skip_records': skip_records}
        par2 = {'id': current_user.id}
        for row in db_sess.execute(statement_count, par2):
            max_page = max(ceil(row[0] / amount_records_page), 1)
            amount_records = row[0]
        if page > max_page: return abort(404)

        for row in db_sess.execute(statement, par):
            work_time = get_work_time(row[1], row[2])
            dct = {'id': row[4], 
                   'name': row[0],
                   'work_time': work_time,
                   'created_date': db_datetime_formating(row[3])}
            page_recs.append(dct)
        params['records'] = page_recs
        params['amount_records_page'] = amount_records_page
        params['amount_records'] = amount_records
        params['current_page'] = page
        params['max_page'] = max_page
        params['pages'] = get_pages(max_page, page)
    return render_template("records.html", **params)

@app.route('/records_delete/<int:item_id>', methods=['POST'])
def rec_delete(item_id):
    if not current_user.is_authenticated:
        return redirect("/records_list/1")
    dct = request.form
    if "amount_records" in dct and "current_page" in dct and "amount_records_page" in dct:
        delete_record(item_id, current_user)
        recs, cur_p, recs_p = dct["amount_records"], dct["current_page"], dct["amount_records_page"]
        p = get_page_after_delete(int(recs), int(cur_p), int(recs_p))
        return redirect(f'/records_list/{p}')
    return redirect('/records_list/1')

"""@app.route('/records_change/<int:item_id>', methods=['POST'])
def rec_change(item_id):
    # change_record(item_id)
    return redirect('/records_list/1')"""

@app.route('/reports_all', methods=['GET', 'POST'])
def multi_bar():
    params = {'title': 'Отчет по дням',
              'description1': 'Отчет по дням',
              'description2': 'Сначала войдите в аккаунт или заведите новый.',
              'status_page': 3}
    if current_user.is_authenticated:
        """dt = datetime(2022, 2, 2)  # comment from
        acts = ['Пузение', 'Жужжание', 'Лежание', 'Поедание']

        for i in range(100):
            dt += timedelta(days=1)
            for _ in range(random.randint(1,6)):
              a = random.choice(acts)
              t = random.random()*3
              data.append([dt, a, t])  # comment to (in get charts)"""
        recs, params, db_sess = get_chart_records(MULTI_BAR, params)
        data = []
        act_names = []
        act_colors = []
        for record in recs:
            a = record.act_n.name
            c = record.act_n.color
            if a not in act_names:
                act_names.append(a)
                act_colors.append(c)
            t = round(record.work_hours + record.work_min/60, 2)
            data.append([record.created_date.date(), a, t])

        # Convert list to dataframe and assign column values
        df = pd.DataFrame(data, columns=['Дата', 'Активность', 'Часы'])
        adj = df.groupby(['Дата', 'Активность'])['Часы'].sum().reset_index()
        # Create Bar chart

        fig = px.bar(adj, x='Дата', y='Часы', color='Активность', 
                     color_discrete_sequence=act_colors, barmode='stack')
        
        fig.update_layout(xaxis=dict(tickformat="%d.%m.%y"))
        #fig.update_xaxes(nticks=df['Дата'].nunique()) 

        # Create graphJSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        db_sess.close()
        # Use render_template to pass graphJSON to html
        return render_template('reports_sum.html', graphJSON=graphJSON, success='Done', **params)
    return render_template("reports_sum.html", **params)

@app.route('/reports_summary', methods=['GET', 'POST'])
def horizontal_bar():
    params = {'title': 'Суммарный отчет',
              'description1': 'Суммарный отчет',
              'description2': 'Сначала войдите в аккаунт или заведите новый.',
              'error': '',
              'status_page': 2}
    if current_user.is_authenticated:
        recs, params, db_sess = get_chart_records(HORIZONTAL_BAR, params)
        activities = []
        act_names = []
        act_colors = []
        for item in recs:
            a, c = item.act_n.name, item.act_n.color
            activities.append([item.act_n.name, item.work_hours + item.work_min / 60, 'None'])
            if a not in act_names:
                act_names.append(a)
                act_colors.append(c)

        df = pd.DataFrame(activities,
                        columns=['Активности', 'Часы', 'Группа'])
        fig = px.bar(df, x='Часы', y='Активности', color='Активности', 
                     barmode='group', color_discrete_sequence=act_colors, orientation='h')

        ttl = df.groupby(['Активности'])['Часы'].sum()
        values = [v for v in ttl]
        keys = list(ttl.keys())
        zipped = zip(keys, values)

        total_labels = [{"x": data, "y": name, "text": f'{data:.2f}', "showarrow": False} for name, data in zipped]
        fig.update_layout(annotations=total_labels)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        db_sess.close()
        
        return render_template("reports_sum.html", graphJSON=graphJSON, **params)
    return render_template("reports_sum.html", **params)

@app.route('/profile_image')
def profile_image():
    if current_user.is_authenticated:
        with db_session.create_session() as db_sess:
            images = db_sess.query(Pictures).filter_by(user_id=current_user.id).all()
            if images:
                response = make_response(images[0].data)
                response.headers.set('Content-Type', 'image/jpeg')
                response.headers.set(
                    'Content-Disposition', 'attachment', filename=f'{images[0].user_id}.jpg')
                return response
            return abort(404)
    return None

@app.route('/profile', methods=['GET', 'POST'])
def profile_page():
    params = {'title': 'Профиль',
              'description1': 'Профиль пользователя',
              'description2': 'Сначала войдите в аккаунт или заведите новый.',
              'status_page': 4}
    if current_user.is_authenticated:
        form = TokenForm()

        params['form'] = form
        params['description2'] = ''
        params['login'] = current_user.login
        params['username'] = current_user.name
        params['date'] = current_user.created_date.strftime('%d/%m/%Y, %H:%M:%S')

        with db_session.create_session() as db_sess:
            db_sess.add(current_user)

            params['all_time'] = str(
                round(sum([item.work_hours + item.work_min / 60 
                for item in db_sess.query(Records).filter(
                Records.user == current_user).all()]), 2))
            if 'submit' in request.form and request.method == 'POST':
                current_user.token = get_token(N_SYMBOLS)
                db_sess.commit()
                return redirect('/profile')
            else:
                params['token'] = current_user.token
    return render_template('profile.html', **params)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with db_session.create_session() as db_sess:
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
        with db_session.create_session() as db_sess:
            if db_sess.query(User).filter(User.login == form.login.data).first():
                return render_template('register.html', title='Регистрация',
                                    form=form,
                                    message="Такой пользователь уже есть")
            user = User(name=form.name.data, login=form.login.data, token=get_token(N_SYMBOLS))
            user.set_password(form.password.data)
            base_acts = [Activities_names(name="Первое занятие", color="#000000"), 
                         Activities_names(name="Вторая активность"), 
                         Activities_names(name="Третья деятельность", color="#42a1f5")]
            for activity in base_acts:
                user.act_names.append(activity)
            db_sess.add(user)
            db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

"""@app.errorhandler(404)
def not_found(error):
    return render_template('error_404.html', title='Страница не найдена', error=error)"""

"""@app.errorhandler(500)
def internal_error(error):
    return render_template('error_500.html', title='Oшибка сервера', error=error)"""

def main():
    db_session.global_init("C:/Dev/Olymps/yandex_lyceum/Project3/db/time_mngr_data.db")
    app.run()

if __name__ == '__main__':
    main()