from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class UniverFindStudentForm(FlaskForm):
    find_student_id = StringField(
        'ID студента',
        validators=[DataRequired()]
    )
    find_submit = SubmitField('Найти')
    find_clear = SubmitField('Стереть')
