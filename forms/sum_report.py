from flask_wtf import FlaskForm
from wtforms import DateField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Optional
from utilities import date_max, date_min


class ReportChartForm(FlaskForm):
    from_date = DateField('С какой даты', format="%Y-%m-%d", validators=[Optional()], default=date_min())
    to_date = DateField('По какую дату', format="%Y-%m-%d", validators=[Optional()], default=date_max())
    activities = SelectMultipleField('Показываемые активности', validators=[DataRequired()])
    to_default = SubmitField("Сбросить параметры")
    submit = SubmitField('Подтвердить')