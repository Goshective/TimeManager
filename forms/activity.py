from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional
from wtforms.widgets import ColorInput


class ActivityForm(FlaskForm):
    name = StringField('Название активности', validators=[DataRequired()])
    color = StringField('Цвет графика', widget=ColorInput(), validators=[Optional()])
    submit = SubmitField('Подтвердить')