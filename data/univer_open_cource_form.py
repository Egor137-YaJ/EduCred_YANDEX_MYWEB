from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class UniverOpenCourseForm(FlaskForm):
    student_id = StringField(
        'ID студента',
        validators=[DataRequired()]
    )
    title_course = StringField("Название курса:", validators=[DataRequired()])
    submit = SubmitField('Открыть курс')
