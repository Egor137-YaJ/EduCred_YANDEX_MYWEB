from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField, DateField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Regexp, Email, ValidationError
import re


def password_complexity(form, field):
    pwd = field.data
    errors = []
    if len(pwd) < 8:
        errors.append("не менее 8 символов")
    if not re.search(r'[A-ZА-Я]', pwd):
        errors.append("заглавную букву")
    if not re.search(r'[a-zа-я]', pwd):
        errors.append("строчную букву")
    if not re.search(r'\d', pwd):
        errors.append("цифру")
    if not re.search(r'\W', pwd):
        errors.append("спецсимвол")
    if errors:
        raise ValidationError(
            "Пароль должен содержать: " + ", ".join(errors))


class RegisterStudentForm(FlaskForm):
    NSP = StringField('ФИО (через пробел)', validators=[
        DataRequired(),
        Regexp(r'^[А-ЯЁа-яёA-Za-z]+\s+[А-ЯЁа-яёA-Za-z]+\s+[А-ЯЁа-яёA-Za-z]+$',
               message='Введите корректное ФИО: фамилия, имя и отчество через пробел')
    ])
    born_date = DateField('Дата рождения', validators=[DataRequired()])
    phone_number = StringField('Номер телефона',
                               validators=[
                                   DataRequired(),
                                   Regexp(r'^(?:\+7|8)\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}$')
                               ])
    about = StringField('О себе', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired(), Email('Некорректный email')])
    password = PasswordField('Пароль', validators=[DataRequired(), password_complexity])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    smart_token = StringField('', render_kw={'type': 'hidden'}, name='smart-token')
    submit = SubmitField('Подтвердить')
