from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


# форма авторизации пользователей
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    smart_token = StringField('', render_kw={'type': 'hidden'}, name='smart-token')
    submit = SubmitField('Sign in')
