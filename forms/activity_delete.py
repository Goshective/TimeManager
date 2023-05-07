from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired


class ActivityDeleteForm(FlaskForm):
    choose_names = SelectField('Выберите активность', validators=[DataRequired()], id='pick_activity')
    check_correctness = BooleanField('Подтверждаю, что хочу удалить активность', validators=[DataRequired()])
    submit = SubmitField('Удалить')