from flask_wtf import FlaskForm
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

IMAGES = tuple('jpg jpe jpeg png gif svg bmp'.split())

class PhotoForm(FlaskForm):
    photo = FileField("Выбрать картинку", validators=[FileAllowed(IMAGES, 'Файл должен быть картинкой'), FileRequired('Файл не должен быть пустым')])
    submit = SubmitField('Загрузить')