from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TelField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError
import re

choices = ['Академия', 'Университет', 'Институт',
           'Техникум', 'Гимназия', 'Школа', 'Лицей',
           'Коллледж', 'Училище', 'Онлайн-курс', 'Другое']


# валидатор для поля с выбором ответа из списка
def validate_choice(form, field):
    if field.data not in [choice[0] for choice in field.choices]:
        raise ValidationError('Invalid choice selected.')


# валидатор сложности пароля
def password_complexity(form, field):
    pwd = field.data or ''
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


# форма профиля для студента
class StudentProfileForm(FlaskForm):
    student_nsp = StringField('ФИО', validators=[DataRequired(message="Укажите ФИО")])
    born = DateField(
        'Дата рождения',
        format='%d.%m.%Y',
        validators=[Optional()]
    )
    phone_num = TelField('Номер телефона', validators=[DataRequired(message="Укажите номер телефона")])
    about = TextAreaField('О себе', validators=[Optional()])
    email = StringField(
        'Email',
        render_kw={'readonly': True, 'class': 'form-control-plaintext'},
        validators=[Email(message="Неверный формат почты")]
    )
    current_password = PasswordField("Введите текущий пароль", validators=[DataRequired()])
    new_password = PasswordField('Пароль', validators=[Optional(), password_complexity])
    new_password_confirm = PasswordField('Подтверждение пароля', validators=[
        EqualTo('new_password', message="Пароли не совпадают")
    ]
                                         )
    submit = SubmitField('Сохранить')


# форма профиля для работодателя
class EmployerProfileForm(FlaskForm):
    INN = StringField('ИНН', render_kw={'readonly': True, 'class': 'form-control-plaintext'})
    title = StringField('Название', render_kw={'readonly': True, 'class': 'form-control-plaintext'})
    boss_nsp = StringField('ФИО руководителя', validators=[Optional()])
    scope = StringField('Специализация', validators=[Optional()])
    address = StringField('Адрес', validators=[Optional()])
    email = StringField(
        'Email',
        render_kw={'readonly': True, 'class': 'form-control-plaintext'},
        validators=[Email()]
    )
    current_password = PasswordField("Введите текущий пароль", validators=[DataRequired()])
    new_password = PasswordField('Пароль', validators=[Optional(), password_complexity])
    new_password_confirm = PasswordField('Подтверждение пароля', validators=[
        EqualTo('new_password', message="Пароли не совпадают")
    ])
    submit = SubmitField('Сохранить')


# форма профиля для оу
class UniversityProfileForm(FlaskForm):
    INN = StringField('ИНН', render_kw={'readonly': True, 'class': 'form-control-plaintext'})
    title = StringField('Название', render_kw={'readonly': True, 'class': 'form-control-plaintext'})
    boss_nsp = StringField('ФИО руководителя', validators=[Optional()])
    type = SelectField('Тип образовательного учреждения', choices=list(map(lambda x: (str(x[0]), x[1]),
                                                                           list(enumerate(choices, 1)))),
                       validators=[DataRequired(), validate_choice])
    address = StringField('Адрес', validators=[Optional()])
    email = StringField(
        'Email',
        render_kw={'readonly': True, 'class': 'form-control-plaintext'},
        validators=[Email()]
    )
    current_password = PasswordField("Введите текущий пароль", validators=[DataRequired()])
    new_password = PasswordField('Пароль', validators=[Optional(), password_complexity])
    new_password_confirm = PasswordField('Подтверждение пароля', validators=[
        EqualTo('new_password', message="Пароли не совпадают")
    ])
    submit = SubmitField('Сохранить')
