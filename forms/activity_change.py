from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional
from wtforms.widgets import ColorInput


class Activity_change_form(FlaskForm):
    choose_name = SelectField('Выберите активность', validators=[DataRequired()])
    name = StringField('Название активности', validators=[DataRequired()])
    color = StringField('Цвет графика', widget=ColorInput(), validators=[Optional()])
    submit = SubmitField('Подтвердить')