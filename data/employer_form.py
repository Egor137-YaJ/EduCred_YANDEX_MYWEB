from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp

class StudentSearchForm(FlaskForm):
    student_id = StringField("ID студента", validators=[
        DataRequired(),
        Regexp(r'^\d+$', message="ID должен быть числом.")
    ])
    submit = SubmitField("Готово")
    invite = SubmitField("Пригласить на собеседование")