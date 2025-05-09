import os
from flask import Flask, render_template, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash

from data import db_session
from data.employer_find_student_form import EmplStudentSearchForm
from data.univer_find_student_form import UniverFindStudentForm
from data.reg_Univer import RegisterUniverForm, choices
from data.reg_Student import RegisterStudentForm
from data.reg_Employer import RegisterEmployerForm
from data.login_form import LoginForm
from data.Users import User
from data.Students import Student
from data.upload_music_form import UploadMusicForm
from data.Universities import University
from data.Employers import Employer
from data.Achievements import Achievement
from data.find_info_by_INN import get_info_by_inn
from data.ProfileForms import StudentProfileForm, EmployerProfileForm, UniversityProfileForm
from data.config import secret_token

app = Flask(__name__)
app.config["SECRET_KEY"] = secret_token

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
    logout_user()
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

        title, address, boss_nsp, check = get_info_by_inn(form.INN.data)
        type = dict(form.type.choices).get(form.type.data)
        if 'Ошибка' in ' '.join([title, address, boss_nsp]):
            return render_template('register_university.html', title='University Registration',
                                   form=form, style=url_for('static', filename='css/style.css'),
                                   message="Error in INN request - may be non existing INN")

        if type.lower() not in ['онлайн-курс', 'другое']:
            if type.lower() not in check.lower():
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
        if ';' in title:
            title = title.split(';')[1]
        elif ',' in title:
            title = title.split(', ')[1]
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
        login_user(user)
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

        title, address, boss_nsp, check = get_info_by_inn(form.INN.data)
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
        login_user(user)
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
        login_user(user)
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
            login_user(user)
            return redirect('/workspace')
        return render_template('login.html', message="Wrong login or password",
                               form=form, style=url_for('static', filename='css/style.css'))
    return render_template('login.html', title='Authorization',
                           form=form, style=url_for('static', filename='css/style.css'))


@app.route('/university_workspace', methods=['POST', 'GET'])
@login_required
def university_workspace():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    univer = user.university
    form = UniverFindStudentForm()
    if form.validate_on_submit():
        student_id = str(form.student_id.data)
        if not student_id.isdigit():
            return render_template('university_workspace.html', form=form, courses=[],
                                   message='ID должен состоять только из цифр',
                                   joined_title=univer.title, student='',
                                   style=url_for('static', filename='css/style.css'))
        student_id = int(student_id)
        db_sess = db_session.create_session()
        courses = db_sess.query(Achievement).filter(
            Achievement.student_id == student_id, Achievement.end_date == None).all()
        student = db_sess.query(Student).filter(Student.id == student_id).first()
        return render_template('university_workspace.html', form=form, courses=courses, message='',
                               student=student,
                               joined_title=univer.title,
                               style=url_for('static', filename='css/style.css'))
    return render_template('university_workspace.html', form=form, courses=[], message='', student='',
                           joined_title=univer.title, style=url_for('static', filename='css/style.css'))


@app.route('/employer_workspace', methods=['GET', 'POST'])
@login_required
def employer_workspace():
    achievements_data = []
    student_fullname = None
    form = EmplStudentSearchForm()

    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    employer = user.employer

    if form.validate_on_submit():
        if form.clear.data:
            return redirect(url_for('employer_workspace'))

        if form.submit.data:
            entered_student_id = form.student_id.data.strip()
            student = db_sess.query(Student).filter(Student.id == entered_student_id).first()

            if not student:
                flash("Студент с таким ID не найден.", "danger")
            else:
                student_fullname = student.student_nsp.strip()
                achievements = db_sess.query(Achievement).filter(
                    Achievement.student_id == student.id,
                    Achievement.end_date != None).all()

                if not achievements:
                    flash("У студента нет достижений.", "warning")
                else:
                    for a in achievements:
                        university = db_sess.query(University).filter(University.id == a.university_id).first()
                        achievements_data.append({
                            'token': a.token,
                            'description': a.title,
                            'university_title': university.title if university else "",
                            'student_id': student.id,
                            'file_path': a.file_path
                        })
                    session['student_id_current'] = student.id
                    session['entered_student_id_current'] = entered_student_id

        elif form.invite.data:
            student = db_sess.query(Student).get(session.pop('student_id_current'))
            entered_student_id = session.pop('entered_student_id_current')
            if not student:
                flash("Невозможно пригласить: студент с таким Id не найден.")
            else:
                if not student.employer_id:
                    student.employer_id = str(employer.id)
                else:
                    ids = set(student.employer_id.split(";"))
                    ids.add(str(employer.id))
                    student.employer_id = ";".join(ids)

                db_sess.commit()
                flash(f"Студент с ID {entered_student_id} приглашён на собеседование.")
                return redirect(url_for('employer_workspace'))

    return render_template("employer_workspace.html",
                           form=form,
                           achievements=achievements_data,
                           joined_title=employer.title,
                           entered_id="" if not form.student_id.data or form.clear.data else entered_student_id,
                           student_fullname=student_fullname,
                           style=url_for('static', filename='css/style.css'))


@app.route('/student_workspace', methods=['GET', 'POST'])
@login_required
def student_workspace():
    achievements_data = []
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    student = user.student
    form = UploadMusicForm()
    if form.validate_on_submit():
        ach = form.audio.data
        # token, path = upload_tokened_ach(ach)
        ach.save(os.path.join('static/achievements', f'{form.name.data}.mp3'))
        achievement = Achievement(
            # token = token,
            # file_path = path,
            file_path=f'achievements/{form.name.data}.mp3',
            title=form.name.data,
            student_id=student.id)
        db_sess.add(achievement)
        db_sess.commit()
        return redirect(url_for('student_workspace'))

    student_fullname = student.student_nsp.strip()
    achievements = db_sess.query(Achievement).filter(
        Achievement.student_id == student.id).all()

    if not achievements:
        flash("У студента нет достижений.", "warning")
    else:
        for a in achievements:
            university = db_sess.query(University).filter(University.id == a.university_id).first()
            achievements_data.append({
                'token': a.token,
                'description': a.title,
                'university_title': university.title if university else "",
                'student_id': student.id,
                'file_path': a.file_path
            })
        session['student_id_current'] = student.id
    return render_template('student_workspace.html',
                           form=form,
                           joined_title=student_fullname,
                           achievements=achievements_data,
                           style=url_for('static', filename='css/style.css'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    born = ''

    if user.role == 'student':
        profile = db_sess.query(Student).filter_by(user_id=user.id).first()
        born = profile.born.strftime('%d.%m.%Y')
        form = StudentProfileForm(obj=profile)
    elif user.role == 'employer':
        profile = db_sess.query(Employer).filter_by(user_id=user.id).first()
        form = EmployerProfileForm(obj=profile)
    else:
        profile = db_sess.query(University).filter_by(user_id=user.id).first()
        form = UniversityProfileForm(obj=profile)
        ch = ['Академия', 'Университет', 'Институт',
              'Техникум', 'Гимназия', 'Школа', 'Лицей',
              'Коллледж', 'Училище', 'Онлайн-курс', 'Другое']
        if profile.type in ch and form.type.data in ch:
            form.type.data = str(ch.index(profile.type) + 1)

    if form.validate_on_submit():
        form.populate_obj(profile)
        if user.role == 'university':
            profile.type = dict(form.type.choices).get(form.type.data)
        pw = form.password.data
        if pw:
            user.set_password(pw)
        try:
            db_sess.commit()
            flash('Профиль успешно обновлён', 'success')
        except Exception as e:
            db_sess.rollback()
            flash('Ошибка при сохранении: ' + str(e), 'danger')
        return redirect(url_for('profile'))
    form.email.data = user.email

    return render_template('profile.html', form=form, role=user.role, title='Личный кабинет', user=user,
                           style=url_for('static', filename='css/style.css'), born=born)


@app.route('/workspace')
@login_required
def workspace():
    user = current_user
    if user.role == 'student':
        login_user(user)
        return redirect("/student_workspace")
    elif user.role == 'university':
        login_user(user)
        return redirect("/university_workspace")
    elif user.role == 'employer':
        login_user(user)
        return redirect("/employer_workspace")
    return redirect('/home')


def main():
    db_session.global_init("db/EduCred_data.db")
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()

    # My web: https://precious-fluoridated-muskox.glitch.me/
    # create git with only this directory on git. just files of that github
    # My Projects: https://glitch.com/dashboard?group=owned&sortColumn=boost&sortDirection=DESC&page=1&showAll=false&filterDomain=
