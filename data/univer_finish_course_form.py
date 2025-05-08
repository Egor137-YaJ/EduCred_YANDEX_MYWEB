from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class UniverCloseCourseForm(FlaskForm):
    close_student_id = StringField("ID студента: ", validators=[DataRequired()])
    close_course_title = StringField("Введите название курса для завершения: ", validators=[DataRequired()])
    close_submit = SubmitField("Закрыть курс")