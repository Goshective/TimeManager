from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional
from wtforms.widgets import ColorInput


class ActivityAddForm(FlaskForm):
    name = StringField('Название активности', validators=[DataRequired()])
    color = StringField('Цвет графика', widget=ColorInput(), validators=[Optional()])
    none_color = BooleanField('Автоматический цвет', validators=[Optional()])
    submit = SubmitField('Добавить')