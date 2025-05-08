from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp


class UniverFindStudentForm(FlaskForm):
    student_id = StringField(
        'ID студента',
        validators=[DataRequired()]
    )
    find_submit = SubmitField('Найти')
