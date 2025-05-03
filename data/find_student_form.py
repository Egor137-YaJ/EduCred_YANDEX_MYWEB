from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp


class FindStudentForm(FlaskForm):
    student_id = StringField(
        'ID студента',
        validators=[DataRequired()]
    )
    submit = SubmitField('Найти')
