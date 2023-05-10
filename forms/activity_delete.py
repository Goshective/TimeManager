from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired


class ActivityDeleteForm(FlaskForm):
    choose_names = SelectField('Выберите активность', validators=[DataRequired()], id='pick_activity')
    submit = SubmitField('Удалить')