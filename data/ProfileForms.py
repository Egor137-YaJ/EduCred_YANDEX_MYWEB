from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TelField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Length, ValidationError

choices = ['Академия', 'Университет', 'Институт',
           'Техникум', 'Гимназия', 'Школа', 'Лицей',
           'Коллледж', 'Училище', 'Онлайн-курс', 'Другое']


def validate_choice(form, field):
    if field.data not in [choice[0] for choice in field.choices]:
        raise ValidationError('Invalid choice selected.')


class StudentProfileForm(FlaskForm):
    student_nsp = StringField('ФИО', validators=[DataRequired(message="Укажите ФИО")])
    born = DateField(
        'Дата рождения',
        format='%d.%m.%Y',
        render_kw={'readonly': True, 'class': 'form-control-plaintext'},
        validators=[]
    )
    phone_num = TelField('Номер телефона', validators=[DataRequired(message="Укажите номер телефона")])
    about = TextAreaField('О себе', validators=[Optional()])
    email = StringField(
        'Email',
        render_kw={'readonly': True, 'class': 'form-control-plaintext'},
        validators=[Email(message="Неверный формат почты")]
    )
    password = PasswordField('Пароль', validators=[Optional(), Length(min=6)])
    confirm = PasswordField('Подтверждение пароля', validators=[
        EqualTo('password', message="Пароли не совпадают")
    ]
                            )
    submit = SubmitField('Сохранить')


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
    password = PasswordField('Пароль', validators=[Optional(), Length(min=6)])
    confirm = PasswordField('Подтверждение пароля', validators=[
        EqualTo('password', message="Пароли не совпадают")
    ])
    submit = SubmitField('Сохранить')


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
    password = PasswordField('Пароль', validators=[Optional(), Length(min=6)])
    confirm = PasswordField('Подтверждение пароля', validators=[
        EqualTo('password', message="Пароли не совпадают")
    ])
    submit = SubmitField('Сохранить')
