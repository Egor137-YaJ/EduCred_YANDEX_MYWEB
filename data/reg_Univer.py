from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, IntegerField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, ValidationError


def validate_choice(form, field):
    if field.data not in [choice[0] for choice in field.choices]:
        raise ValidationError('Invalid choice selected.')


class RegisterUniverForm(FlaskForm):
    INN = IntegerField('ИНН', validators=[DataRequired()])
    type = SelectField('Тип образовательного учреждения', choices=[('1', 'Университет'), ('2', 'Институт'),
                                                                    ('3', 'Школа'), ('4', 'Гимназия'),
                                                                    ('5', 'Лицей'), ('6', 'Интернат'),
                                                                    ('7', 'Училище'), ('8', 'Онлайн-курс'),
                                                                    ('9', 'Кружок'), ('10', 'Секция'),
                                                                    ('11', 'Дополнительное образование')],
                       validators=[DataRequired(), validate_choice])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
