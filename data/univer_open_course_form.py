from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class UniverOpenCourseForm(FlaskForm):
    student_id = StringField(
        'ID студента',
        validators=[DataRequired()]
    )
    course_title = StringField("Название курса:", validators=[DataRequired()])
    open_submit = SubmitField('Открыть курс')
