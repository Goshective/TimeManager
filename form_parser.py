from flask import redirect

from data.act_names import Activities_names
from data.pictures import Pictures
from data import db_session


def add_activity(form, current_user):
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        db_sess.add(current_user)
        activities = Activities_names(name=form.name.data)  # and add color
        current_user.act_names.append(activities)
        db_sess.commit()
        db_sess.close()
        return 0, redirect('/settings')
    else:
        return 1, parser_add_activity_error(form.errors)
    
def parser_add_activity_error(errors):
    return errors

def change_activity():
    pass

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