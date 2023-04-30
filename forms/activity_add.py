from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional
from wtforms.widgets import ColorInput


class Activity_add_form(FlaskForm):
    name = StringField('Название активности', validators=[DataRequired()])
    color = StringField('Цвет графика', widget=ColorInput(), validators=[Optional()])
    submit = SubmitField('Добавить')