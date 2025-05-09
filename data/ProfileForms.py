from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TelField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Length


class StudentProfileForm(FlaskForm):
    student_nsp = StringField('ФИО', validators=[DataRequired(message="Укажите ФИО")])
    born = DateField(
        'Дата рождения',
        format='%d.%m.%Y',
        render_kw={'readonly': True, 'class': 'form-control-plaintext'},
        validators=[Optional()]
    )
    phone_num = TelField('Номер телефона', validators=[Optional()])
    about = TextAreaField('О себе', validators=[Optional()])
    email = StringField(
        'Email',
        render_kw={'readonly': True, 'class': 'form-control-plaintext'},
        validators=[DataRequired(), Email(message="Неверный формат почты")]
    )
    password = PasswordField('Пароль', validators=[DataRequired(message="Введите пароль"), Length(min=6)])
    confirm = PasswordField('Подтверждение пароля', validators=[
        DataRequired(message="Повторите пароль"),
        EqualTo('password', message="Пароли не совпадают")
    ]
                                     )
    submit = SubmitField('Сохранить')


class EmployerProfileForm(FlaskForm):
    INN = StringField('ИНН', render_kw={'readonly': True, 'class': 'form-control-plaintext'})
    title = StringField('Название', render_kw={'readonly': True, 'class': 'form-control-plaintext'})
    boss_nsp = StringField('ФИО руководителе', validators=[DataRequired(message="Укажите ФИО руководителя")])
    scope = StringField('Специализация', validators=[Optional()])
    address = StringField('Адрес', validators=[Optional()])
    email = StringField(
        'Email',
        render_kw={'readonly': True, 'class': 'form-control-plaintext'},
        validators=[DataRequired(), Email()]
    )
    password = PasswordField('Пароль', validators=[DataRequired(message="Введите пароль"), Length(min=6)])
    confirm = PasswordField('Подтверждение пароля', validators=[
        DataRequired(message="Повторите пароль"),
        EqualTo('password', message="Пароли не совпадают")
    ])
    submit = SubmitField('Сохранить')


class UniversityProfileForm(FlaskForm):
    INN = StringField('ИНН', render_kw={'readonly': True, 'class': 'form-control-plaintext'})
    title = StringField('Название', render_kw={'readonly': True, 'class': 'form-control-plaintext'})
    boss_nsp = StringField('ФИО руководителя',
                                     validators=[DataRequired(message="Укажите ФИО руководителя")]
                                     )
    type = StringField('Тип', validators=[Optional()])
    address = StringField('Адрес', validators=[Optional()])
    email = StringField(
        'Email',
        render_kw={'readonly': True, 'class': 'form-control-plaintext'},
        validators=[DataRequired(), Email()]
    )
    password = PasswordField('Пароль', validators=[DataRequired(message="Введите пароль"), Length(min=6)])
    confirm = PasswordField('Подтверждение пароля', validators=[
        DataRequired(message="Повторите пароль"),
        EqualTo('password', message="Пароли не совпадают")
    ])
    submit = SubmitField('Сохранить')
