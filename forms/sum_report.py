from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Optional
from datetime import datetime


class ReportSumForm(FlaskForm):
    from_date = DateField('С', format="%Y-%m-%d", validators=[Optional()], default=(datetime.min))
    to_date = DateField('По', format="%Y-%m-%d", validators=[Optional()], default=datetime.now())
    activities = SelectMultipleField('Показываемые активности', validators=[DataRequired()])
    to_default = BooleanField("Вернуть к обычному состоянию", default=False)
    submit = SubmitField('Подтвердить')