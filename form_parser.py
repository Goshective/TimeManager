from flask import redirect
from sqlalchemy import and_, or_, not_

from data.act_names import Activities_names
from data.records import Records
from data.pictures import Pictures
from data import db_session


def add_activity(form, current_user):
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        clone_detecting = db_sess.query(Activities_names).filter(
            and_(Activities_names.user == current_user, or_(
            Activities_names.name == form.name.data, and_(not_(
            form.none_color.data), 
            Activities_names.color == form.color.data)))).all()
        if clone_detecting:
            db_sess.close()
            return 1, "Такое имя или цвет активности уже существуют"
        db_sess.add(current_user)
        activity = Activities_names(name=form.name.data)
        if not form.none_color.data:
            activity.color = form.color.data
        current_user.act_names.append(activity)
        db_sess.commit()
        db_sess.close()
        return 0, redirect('/settings')
    else:
        return 1, parser_activity_error(form.errors)
    
def parser_activity_error(errors):
    return errors

def change_activity(form, current_user):
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        clone_detecting = db_sess.query(Activities_names).filter(
            and_(Activities_names.user == current_user, or_(
            Activities_names.name == form.name.data, 
            and_((form.choose_color_mode.data == '3'), 
            Activities_names.color == form.color.data),
            ), Activities_names.id != int(form.choose_names.data))).all()
        if clone_detecting:
            db_sess.close()
            return 1, "Такое имя или цвет активности уже существуют"
        db_sess.add(current_user)
        change_detector = False
        if form.choose_color_mode.data == "2":
            db_sess.query(Activities_names).filter(
                Activities_names.id == int(form.choose_names.data)
                ).update({"color": None})
            change_detector = True
        elif form.choose_color_mode.data == "3":
            db_sess.query(Activities_names).filter(
                Activities_names.id == int(form.choose_names.data)
                ).update({"color": form.color.data})
            change_detector = True
        if form.name.data:
            db_sess.query(Activities_names).filter(
                Activities_names.id == int(form.choose_names.data)
                ).update({"name": form.name.data})
            change_detector = True
        if not change_detector:
            return 1, "Вы не выбрали поля для изменения"
        db_sess.commit()
        db_sess.close()
        return 0, redirect('/settings')
    else:
        return 1, parser_activity_error(form.errors)
    
def delete_activity(form, current_user):
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        db_sess.add(current_user)
        
        db_sess.query(Records).filter_by(name_id=int(form.choose_names.data)).delete()
        db_sess.query(Activities_names).filter_by(id=int(form.choose_names.data)).delete()
        db_sess.commit()
        db_sess.close()
        return 0, redirect('/settings')
    else:
        return 1, parser_activity_error(form.errors)

def add_photo(form, current_user):
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        db_sess.add(current_user)
        lst = form.photo.data.stream.read()
        if len(lst) > 1024 ** 2:
            db_sess.close()
            return 1, "Размер файла слишком большой"
        else:
            if current_user.picture:
                current_user.picture.data = lst
            else:
                current_user.picture =  Pictures(data=lst)
            db_sess.commit()
        db_sess.close()
        return 0, redirect('/settings')
    else:
        return 1, parser_photo_error(form.errors)
    
def parser_photo_error(errors):
    if 'photo' in errors:
        return errors['photo'][0]
    return errors