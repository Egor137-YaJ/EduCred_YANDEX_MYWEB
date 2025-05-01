import os
from flask import Flask, render_template, redirect, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user

from data import db_session
from data.reg_Univer import RegisterUniverForm, choices
from data.reg_Student import RegisterStudentForm
from data.reg_Employer import RegisterEmployerForm
from data.login_form import LoginForm
from data.Users import User
from data.Students import Student
from data.Universities import University
from data.Employers import Employer
from data.Achievements import Achievement
from data.find_info_by_INN import get_info_by_inn


app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)


...


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html', title='Home Page', style=url_for('static', filename='css/style.css'))


@app.route('/register_university', methods=['GET', 'POST'])
def register_university():
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

        title, address, boss_nsp = get_info_by_inn(form.INN.data)
        type = dict(form.type.choices).get(form.type.data)
        if 'Ошибка' in ' '.join([title, address, boss_nsp]):
             return render_template('register_university.html', title='University Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Error in INN request - may be non existing INN")

        if type.lower() not in ['онлайн-курс', 'другое']:
            if type.lower() not in title.lower():
                return render_template('register_university.html', title='University Registration',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="Types doesn't match")
        else:
            if any(type_n.lower() in title.lower() for type_n in list(map(str.lower, choices))):
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
        title = title.split(';')[0] if ';' in title else title.split(',')[0]
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
        session['self'] = univer.title
        return redirect('/university_workspace')
    return render_template('register_university.html', title='University Registration',
                           form=form, style=url_for('static', filename='css/style.css'))


@app.route('/register_employer', methods=['GET', 'POST'])
def register_employer():
    form = RegisterEmployerForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_employer.html', title='Employer Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(Employer).filter(Employer.INN == form.INN.data).first():
            return render_template('register_employer.html', title='Employer Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="This Employer already exists")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register_employer.html', title='Employer Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Account with this email already exists")
        if any(user.check_password(form.password.data) for user in db_sess.query(User).all()):
            return render_template('register_employer.html', title='Employer Registration',
                                    form=form, style=url_for('static', filename='css/style.css'),
                                    message="Account with this password already exists")

        title, address, boss_nsp = get_info_by_inn(form.INN.data)
        if 'Ошибка' in ' '.join([title, address, boss_nsp]):
             return render_template('register_employer.html', title='Employer Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Error in INN request - may be non existing INN")

        user = User(
            email=form.email.data,
            role='employer'
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        employer = Employer(
            user_id=user.id,
            INN=form.INN.data,
            title=title,
            address=address,
            boss_nsp=boss_nsp,
            phone_num=form.phone_number.data,
            scope=form.speciality.data,
        )
        db_sess.add(employer)
        db_sess.commit()
        session['self'] = employer.title
        return redirect('/employer_workspace')
    return render_template('register_employer.html', title='Employer Registration',
                           form=form, style=url_for('static', filename='css/style.css'))


@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    form = RegisterStudentForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_student.html', title='Student Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(Student).filter(Student.student_nsp == form.NSP.data,
                                         Student.born == form.born_date.data,
                                         Student.phone_num == form.phone_number.data).first():
            return render_template('register_student.html', title='Student Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="This Student already exists")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register_student.html', title='Student Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Account with this email already exists")
        if any(user.check_password(form.password.data) for user in db_sess.query(User).all()):
            return render_template('register_student.html', title='Student Registration',
                                    form=form, style=url_for('static', filename='css/style.css'),
                                    message="Account with this password already exists")

        if form.born_date.data.year < 1940:
             return render_template('register_student.html', title='Student Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Non existing botn date")

        user = User(
            email=form.email.data,
            role='student'
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        student = Student(
            user_id=user.id,
            student_nsp=form.NSP.data,
            born=form.born_date.data,
            phone_num=form.phone_number.data,
            about=form.about.data,
        )
        db_sess.add(student)
        db_sess.commit()
        session['self'] = student.student_nsp
        return redirect('/student_workspace')
    return render_template('register_student.html', title='Student Registration',
                           form=form, style=url_for('static', filename='css/style.css'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.role == 'student':
                session['self'] = user.student.student_nsp
                return redirect("/student_workspace")
            elif user.role == 'university':
                session['self'] = user.university.title
                return redirect("/university_workspace")
            elif user.role == 'employer':
                session['self'] = user.employer.title
                return redirect("/employer_workspace")
            return redirect('/home')
        return render_template('login.html', message="Wrong login or password",
                               form=form, style=url_for('static', filename='css/style.css'))
    return render_template('login.html', title='Authorization',
                           form=form, style=url_for('static', filename='css/style.css'))


@app.route('/university_workspace')
def university_workspace():
    ...
    return render_template('university_workspace.html',
                           joined_title=session.get('self'), style=url_for('static', filename='css/style.css'))


@app.route('/employer_workspace')
def employer_workspace():
    ...
    return render_template('employer_workspace.html',
                           joined_title=session.get('self'), style=url_for('static', filename='css/style.css'))


@app.route('/student_workspace')
def student_workspace():
    ...
    return render_template('student_workspace.html',
                           joined_title=session.get('self'), style=url_for('static', filename='css/style.css'))


def main():
    db_session.global_init("db/EduCred_data.db")
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()


# My web: https://precious-fluoridated-muskox.glitch.me/
# create git with only this directory on git. just files of that github
# My Projects: https://glitch.com/dashboard?group=owned&sortColumn=boost&sortDirection=DESC&page=1&showAll=false&filterDomain=