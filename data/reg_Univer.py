from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, IntegerField, SelectField, StringField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, ValidationError, equal_to, Email
import re

choices = ['Академия', 'Университет', 'Институт',
           'Техникум', 'Гимназия', 'Школа', 'Лицей',
           'Коллледж', 'Училище', 'Онлайн-курс', 'Другое']


def validate_choice(form, field):
    if field.data not in [choice[0] for choice in field.choices]:
        raise ValidationError('Invalid choice selected.')


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


class RegisterUniverForm(FlaskForm):
    INN = IntegerField('ИНН', validators=[DataRequired()])
    type = SelectField('Тип образовательного учреждения',
                       choices=list(map(lambda x: (str(x[0]), x[1]), list(enumerate(choices, 1)))),
                       validators=[DataRequired(), validate_choice])
    email = EmailField('Почта', validators=[DataRequired(), Email('Некорректный email')])
    password = PasswordField('Пароль', validators=[DataRequired(), password_complexity])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired(), equal_to('password')])
    smart_token = StringField('', render_kw={'type': 'hidden'}, name='smart-token')
    submit = SubmitField('Подтвердить')
