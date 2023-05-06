from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired, Optional
from wtforms.widgets import ColorInput


class ActivityChangeForm(FlaskForm):
    choose_names = SelectField('Выберите активность', validators=[DataRequired()], id='pick_activity')
    name = StringField('Название активности', validators=[Optional()], id='activity_name')
    choose_color_mode = RadioField(
        "", choices=[('1', 'Оставить цвет'), ('2','Автоматический цвет'), 
                     ('3','Выбрать цвет')], validators=[Optional()], default="1")
    color = StringField('Цвет графика', widget=ColorInput(), validators=[Optional()])
    submit = SubmitField('Изменить')