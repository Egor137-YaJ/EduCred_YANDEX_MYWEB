from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired

class UploadProjectForm(FlaskForm):
    name = StringField("Наименование", validators=[DataRequired()])
    file = FileField("Загрузить", validators=[FileRequired('Пустой файл!')])
    univer_title = SelectField("Учреждение", choices=[], validators=[DataRequired()])
    submit = SubmitField("Добавить")

