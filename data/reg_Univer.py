from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, IntegerField, SelectField, StringField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, ValidationError, equal_to


choices = ['Академия', 'Университет', 'Институт',
           'Техникум', 'Гимназия', 'Школа', 'Лицей',
           'Коллледж', 'Училище', 'Онлайн-курс', 'Другое']


def validate_choice(form, field):
    if field.data not in [choice[0] for choice in field.choices]:
        raise ValidationError('Invalid choice selected.')


class RegisterUniverForm(FlaskForm):
    INN = IntegerField('ИНН', validators=[DataRequired()])
    type = SelectField('Тип образовательного учреждения', choices=list(map(lambda x: (str(x[0]), x[1]), list(enumerate(choices, 1)))),
                       validators=[DataRequired(), validate_choice])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired(), equal_to('password')])
    submit = SubmitField('Подтвердить')
