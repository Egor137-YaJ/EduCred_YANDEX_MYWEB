from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired

class UploadMusicForm(FlaskForm):
    name = StringField("Наименование", validators=[DataRequired()])
    audio = FileField("Загрузить", validators=[FileAllowed(tuple('wav mp3 aac ogg oga flac'.split()), 'Только Аудио!'),
                      FileRequired('Пустой файл!')])
    univer_title = SelectField("Учреждение", choices=[], validators=[DataRequired()])
    submit = SubmitField("Добавить")

