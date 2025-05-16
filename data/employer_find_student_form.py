from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# форма поиска студентов работодателем
class EmplStudentSearchForm(FlaskForm):
    student_id = StringField("ID студента", validators=[
        DataRequired()])
    submit = SubmitField("Готово")
    clear = SubmitField("Стереть")
    invite = SubmitField("Пригласить на собеседование")
