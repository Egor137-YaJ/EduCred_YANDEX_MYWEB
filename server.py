import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user

from data import db_session
from data.reg_Univer import RegisterUniverForm
from data.reg_Student import RegisterStudentForm
from data.reg_Employer import RegisterEmployerForm
from data.login_form import LoginForm
from data.Users import User
from data.Students import Student
from data.Universities import University
from data.Employers import Employer
from data.Achievements import Achievement
from data.find_info_by_INN import get_university_info_by_inn


app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"

# login_manager = LoginManager()
# login_manager.init_app(app)

...



@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html', title='Home Page')


@app.route('/register_university', methods=['GET', 'POST'])
def reqister_university():
    form = RegisterUniverForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_university.html', title='University Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Passwords don't match")
        db_sess = db_session.create_session()

        if db_sess.query(University).filter(University.INN == form.INN.data).first():
            return render_template('register_university.html', title='University Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="This University already exists")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register_university.html', title='University Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Account with this email already exists")
        if any(user.check_password(form.password.data) for user in db_sess.query(User).all()):
            return render_template('register_university.html', title='University Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Account with this password already exists")

        title, address, boss_nsp = get_university_info_by_inn(form.INN.data)
        type = dict(form.type.choices).get(form.type.data)

        if 'Ошибка' in ' '.join([title, address, boss_nsp]):
            return render_template('register_university.html', title='University Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Error in INN request - may be non existing INN")

        if type.lower() not in title.lower():
            return render_template('register_university.html', title='University Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Types doesn't match")

        user = User(
            email=form.email.data,
            role='university'
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        univer = University(
            user_id=user.id,
            INN=form.INN.data,
            title=title,
            address=address,
            boss_nsp=boss_nsp,
            type=type
        )
        db_sess.add(univer)
        db_sess.commit()
        return redirect('/home')
    return render_template('register_university.html', title='University Registration',
                           form=form, style=url_for('static', filename='css/style.css'))


...


def main():
    db_session.global_init("db/EduCred_data.db")
    # port = int(os.environ.get("PORT", 8000))
    # app.run(host='0.0.0.0', port=port)
    app.run()


if __name__ == '__main__':
    main()


# My web: https://precious-fluoridated-muskox.glitch.me/
# create git with only this directory on git. just files of that github
# My Projects: https://glitch.com/dashboard?group=owned&sortColumn=boost&sortDirection=DESC&page=1&showAll=false&filterDomain=