from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField, DateField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Regexp


class RegisterStudentForm(FlaskForm):
    NSP = StringField('ФИО(через пробел)', validators=[DataRequired()])
    born_date = DateField('Дата рождения', validators=[DataRequired()])
    phone_number = StringField('Номер телефона',
                        validators=[
                            DataRequired(),
                            Regexp(r'^(?:\+7|8)\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}$')
                        ])
    about = StringField('О себе', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')