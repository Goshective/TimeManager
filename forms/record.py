from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional


class RecordForm(FlaskForm):
    date = DateField('Дата выполнения', format="%Y-%m-%d", validators=[DataRequired()])
    activity = SelectField('Выберите активность', validators=[DataRequired()])
    work_hour = IntegerField('Количество часов', validators=[Optional()], default=0)
    work_min = IntegerField('Количество минут', validators=[Optional()], default=0)
    submit = SubmitField('Подтвердить')