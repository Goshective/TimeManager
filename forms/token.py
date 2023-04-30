from flask_wtf import FlaskForm
from wtforms import SubmitField


class TokenForm(FlaskForm):
    submit = SubmitField('Изменить токен')