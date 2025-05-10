import datetime
import os
from flask import Flask, render_template, redirect, url_for, session, flash, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import or_
from sqlalchemy.testing import not_in

from data import db_session
from data.employer_find_student_form import EmplStudentSearchForm
from data.univer_find_student_form import UniverFindStudentForm
from data.univer_open_course_form import UniverOpenCourseForm
from data.univer_finish_course_form import UniverCloseCourseForm
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
from data.cert_creating import tokenize, pdf_creating
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
    form_find = UniverFindStudentForm()
    form_open = UniverOpenCourseForm()
    form_close = UniverCloseCourseForm()
    courses = []
    student_find_table = ''
    projs = db_sess.query(Achievement).filter(Achievement.university_id == univer.id,
                                              or_(Achievement.end_date == None,
                                                  Achievement.end_date == ""),
                                              Achievement.approve_path == None
                                              ).all()

    if form_find.validate_on_submit():
        if form_find.find_submit.data:
            student_id = str(form_find.find_student_id.data)
            if not student_id.isdigit():
                flash('ID студента, которого вы хотите найти, должен состоять только из цифр', "warning")
            student_id = int(student_id)
            db_sess = db_session.create_session()
            student_find_table = db_sess.query(Student).filter(Student.id == student_id).first()
            if not student_find_table:
                flash("Неверное ID студента для поиска", "warning")
            courses = db_sess.query(Achievement).filter(
                Achievement.student_id == student_id,
                or_(Achievement.end_date == None,
                    Achievement.end_date == "")
            ).all()

    if form_open.validate_on_submit():
        if form_open.open_submit.data:
            student_id = str(form_open.open_student_id.data)
            if not student_id.isdigit():
                flash('ID студента, которому вы хотите открыть курс, должен состоять только из цифр', "warning")
            student_id = int(student_id)
            db_sess = db_session.create_session()
            new_ach = Achievement(
                title=str(form_open.open_course_title.data),
                start_date=datetime.datetime.now(),
                student_id=student_id,
                university_id=univer.id,
                approve_path='Not Required'
            )
            db_sess.add(new_ach)
            db_sess.commit()
            flash(f"Курс для студента с ID {student_id} открыт успешно, удачи!", "success")
            return redirect(url_for('university_workspace'))

    if form_close.validate_on_submit():
        if form_close.close_submit.data:
            student_id = str(form_close.close_student_id.data)
            if not student_id.isdigit():
                flash('ID студента, которому вы хотите завершить курс, должен состоять только из цифр', "warning")
            student_id = int(student_id)

            got_title = str(form_close.close_course_title.data)
            db_sess = db_session.create_session()
            found_course = db_sess.query(Achievement).filter(
                Achievement.title == got_title,
                or_(Achievement.end_date == None,
                    Achievement.end_date == ""),
                Achievement.university_id == univer.id,
                Achievement.student_id == student_id,
                Achievement.approve_path == 'Not Required'
            ).first()
            if found_course:
                token = tokenize()
                found_course.token = token
                found_course.end_date = datetime.datetime.now()
                file_path = pdf_creating(student_nsp=found_course.student.student_nsp,
                                         course_title=found_course.title,
                                         univer_title=univer.title,
                                         start_date=found_course.start_date,
                                         end_date=found_course.end_date,
                                         univer_boss=univer.boss_nsp,
                                         token=token)
                found_course.file_path = file_path
                db_sess.commit()
                flash(f"Курс закрыт успешно, поздравляем! Токен: {token}.", "success")
                return redirect(url_for('university_workspace'))
            else:
                flash("Неверные данные для закрытия курса", "warning")

    return render_template('university_workspace.html',
                           form_find=form_find, form_close=form_close, form_open=form_open,
                           student_find=student_find_table,
                           courses=courses,
                           projs=projs,
                           joined_title=univer.title,
                           style=url_for('static', filename='css/style.css'))


@app.route('/manage_proj', methods=["POST"])
@login_required
def manage_proj():
    db_sess = db_session.create_session()
    proj_id = request.form.get('project_id')
    action = request.form.get('action')
    proj = db_sess.query(Achievement).get(proj_id)

    if not proj:
        abort(404)

    if action == 'reject':
        db_sess.delete(proj)
        db_sess.commit()
        flash("Проект отклонён и удалён", "info")

    elif action == 'approve':
        token = tokenize()
        proj.token = token
        proj.end_date = datetime.datetime.now()
        proj.approve_path = pdf_creating(student_nsp=proj.student.student_nsp,
                                         course_title=proj.title,
                                         univer_title=proj.university.title,
                                         start_date=proj.start_date,
                                         end_date=proj.end_date,
                                         univer_boss=proj.university.boss_nsp,
                                         token=proj.token,
                                         mark="approved",
                                         type="proj")
        db_sess.commit()
        flash("Проект подтверждён, сертификат подтверждения добавлен!", "success")

    return redirect(url_for('university_workspace'))


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
                    Achievement.end_date.isnot(None),
                    Achievement.end_date != ""
                ).all()

                if not achievements:
                    flash("У студента нет достижений.", "warning")
                else:
                    for a in achievements:
                        university = db_sess.query(University).filter(University.id == a.university_id).first()
                        achievements_data.append({
                            'token': a.token,
                            'title': a.title,
                            'university_title': university.title if university else "",
                            'student_id': student.id,
                            'file_path': a.file_path,
                            'approve': a.approve_path
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
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    student = user.student
    form = UploadMusicForm()
    approved_achievements_data = []
    nonapproved_achievements_data = []
    active_courses_data = []
    inactive_courses_data = []
    employers_data = []
    student_fullname = student.student_nsp.strip()

    univers = db_sess.query(University).all()
    form.univer_title.choices = [(u.title, u.title) for u in univers]
    if form.validate_on_submit():
        ach = form.audio.data
        ach.save(os.path.join('static/achievements', f'{form.name.data}.mp3'))
        short_path = os.path.join('achievements', f'{form.name.data}.mp3')
        chosen_univer = db_sess.query(University).filter(University.title == form.univer_title.data).first()
        achievement = Achievement(
            file_path=short_path,
            title=form.name.data,
            start_date=datetime.datetime.now(),
            student_id=student.id,
            university_id=chosen_univer.id
        )
        db_sess.add(achievement)
        db_sess.commit()
        return redirect(url_for('student_workspace'))

    employers_ids = list(map(int, student.employer_id.split(';')))

    employers = db_sess.query(Employer).filter(
        Employer.id.in_(employers_ids)
    ).all()

    for e in employers:
        employers_data.append({
            'INN': e.INN,
            'title': e.title,
            'address': e.address,
            'boss_nsp': e.boss_nsp,
            'phone_num': e.phone_num
        })

    approved_achievements = db_sess.query(Achievement).filter(
        Achievement.student_id == student.id,
        Achievement.approve_path.isnot(None),
        Achievement.approve_path != "Not Required"
    ).all()

    nonapproved_achievements = db_sess.query(Achievement).filter(
        Achievement.student_id == student.id,
        Achievement.approve_path.is_(None)
    ).all()

    active_courses = db_sess.query(Achievement).filter(
        Achievement.student_id == student.id,
        Achievement.approve_path == "Not Required",
        Achievement.end_date.is_(None),
    ).all()

    inactive_courses = db_sess.query(Achievement).filter(
        Achievement.student_id == student.id,
        Achievement.end_date.isnot(None),
        Achievement.end_date != "",
        Achievement.approve_path == "Not Required"
    ).all()

    # if not (approved_achievements or nonapproved_achievements or active_courses or inactive_courses):
    #     flash("У студента нет достижений.", "warning")
    # else:
    for a in approved_achievements:
        university = db_sess.query(University).filter(University.id == a.university_id).first()
        approved_achievements_data.append({
            'token': a.token,
            'title': a.title,
            'university_title': university.title if university else "",
            'student_id': student.id,
            'file_path': a.file_path,
            'approve': a.approve_path
        })

    for a in nonapproved_achievements:
        university = db_sess.query(University).filter(University.id == a.university_id).first()
        nonapproved_achievements_data.append({
            'title': a.title,
            'university_title': university.title if university else "",
            'student_id': student.id,
            'file_path': a.file_path,
        })

    for a in active_courses:
        university = db_sess.query(University).filter(University.id == a.university_id).first()
        active_courses_data.append({
            'title': a.title,
            'university_title': university.title if university else "",
            'student_id': student.id,
        })

    for a in inactive_courses:
        university = db_sess.query(University).filter(University.id == a.university_id).first()
        inactive_courses_data.append({
            'token': a.token,
            'title': a.title,
            'university_title': university.title if university else "",
            'student_id': student.id,
            'file_path': a.file_path,
        })
    session['student_id_current'] = student.id
    return render_template('student_workspace.html',
                           form=form,
                           joined_title=student_fullname,
                           approved_achievements=approved_achievements_data,
                           nonapproved_achievements=nonapproved_achievements_data,
                           active_courses=active_courses_data,
                           inactive_courses=inactive_courses_data,
                           employers=employers_data,
                           style=url_for('static', filename='css/style.css'))


def main():
    db_session.global_init("db/EduCred_data.db")
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()

    # My web: https://precious-fluoridated-muskox.glitch.me/
    # create git with only this directory on git. just files of that github
    # My Projects: https://glitch.com/dashboard?group=owned&sortColumn=boost&sortDirection=DESC&page=1&showAll=false&filterDomain=
