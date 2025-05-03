from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp


class FindStudentForm(FlaskForm):
    student_id = StringField(
        'ID студента',
        validators=[
            DataRequired(message="Поле ID студента не может быть пустым"),
            Regexp(r'^\d+$', message="ID должен состоять только из цифр")
        ]
    )
    submit = SubmitField('Найти')
