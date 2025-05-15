import datetime
import os
import random
from flask import Flask, render_template, redirect, url_for, session, flash, request, abort, send_from_directory, \
    send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import or_
from werkzeug.utils import secure_filename
import logging

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
from data.upload_project_form import UploadProjectForm
from data.Universities import University
from data.Employers import Employer
from data.Achievements import Achievement
from data.find_info_by_INN import get_info_by_inn
from data.cert_creating import tokenize, pdf_creating
from data.ProfileForms import StudentProfileForm, EmployerProfileForm, UniversityProfileForm
from data.config import secret_token

app = Flask(__name__)
app.config["SECRET_KEY"] = secret_token

login_manager = LoginManager()
login_manager.init_app(app)

formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(message)s')

file_handler = logging.FileHandler('logs.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

app.logger.addHandler(file_handler)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/home', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def home():
    logout_user()
    try:
        db_sess = db_session.create_session()
        token = None
        achievement = None
        university = None

        if request.method == 'POST':
            token = request.form.get('token', '').strip()
            if not token:
                flash('Введите токен достижения', 'warning')
            else:
                achievement = db_sess.query(Achievement).filter_by(token=token).first()
                if not achievement:
                    flash(f'Достижение с токеном «{token}» не найдено.', 'danger')
                else:
                    if achievement.end_date is None:
                        flash(
                            f'{achievement.student.student_nsp} проходит курс «{achievement.title}»'
                            ', но ещё не окончил(а).', 'info')
                    university = db_sess.query(University).filter_by(id=achievement.university_id).first()

        return render_template(
            'home.html',
            token=token,
            achievement=achievement,
            university=university,
            title='Главная'
        )
    except Exception as e:
        flash(f'Произошла неизвестная ошибка, попробуйте ещё раз', 'danger')
        app.logger.error(e)
        return render_template('home.html', token=None, result=None, university=None, title='Главная')


@app.route('/register_university', methods=['GET', 'POST'])
def register_university():
    form = RegisterUniverForm()
    try:
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register_university.html',
                                       title='Регистрация образовательного учреждения',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="Passwords don't match")
            db_sess = db_session.create_session()
            if db_sess.query(University).filter(University.INN == form.INN.data).first():
                return render_template('register_university.html',
                                       title='Регистрация образовательного учреждения',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="This University already exists")
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register_university.html',
                                       title='Регистрация образовательного учреждения',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="Account with this email already exists")
            if any(user.check_password(form.password.data) for user in db_sess.query(User).all()):
                return render_template('register_university.html',
                                       title='Регистрация образовательного учреждения',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="Account with this password already exists")

            title, address, boss_nsp, check = get_info_by_inn(form.INN.data)
            type = dict(form.type.choices).get(form.type.data)
            if 'Ошибка' in ' '.join([title, address, boss_nsp]):
                return render_template('register_university.html',
                                       title='Регистрация образовательного учреждения',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="Error in INN request - may be non existing INN")

            if type.lower() not in ['онлайн-курс', 'другое']:
                if type.lower() not in check.lower():
                    return render_template('register_university.html',
                                           title='Регистрация образовательного учреждения',
                                           form=form, style=url_for('static', filename='css/style.css'),
                                           message="Types doesn't match")
            else:
                if any(type_n.lower() in title.lower() for type_n in list(map(str.lower, choices))):
                    return render_template('register_university.html',
                                           title='Регистрация образовательного учреждения',
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
    except Exception as e:
        app.logger.error('An error occurred: %s', e)
        flash('Произошла неизвестная ошибка, попробуйте ещё раз', 'danger')
    return render_template('register_university.html',
                           title='Регистрация образовательного учреждения',
                           form=form, style=url_for('static', filename='css/style.css'))


@app.route('/register_employer', methods=['GET', 'POST'])
def register_employer():
    form = RegisterEmployerForm()
    try:
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register_employer.html', title='Регистрация работодателя',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="Passwords don't match")
            db_sess = db_session.create_session()
            if db_sess.query(Employer).filter(Employer.INN == form.INN.data).first():
                return render_template('register_employer.html', title='Регистрация работодателя',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="This Employer already exists")
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register_employer.html', title='Регистрация работодателя',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="Account with this email already exists")
            if any(user.check_password(form.password.data) for user in db_sess.query(User).all()):
                return render_template('register_employer.html', title='Регистрация работодателя',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="Account with this password already exists")

            title, address, boss_nsp, check = get_info_by_inn(form.INN.data)
            if 'Ошибка' in ' '.join([title, address, boss_nsp]):
                return render_template('register_employer.html', title='Регистрация работодателя',
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
    except Exception as e:
        app.logger.error('An error occurred: %s', e)
        flash('Произошла неизвестная ошибка, попробуйте ещё раз', 'danger')
    return render_template('register_employer.html', title='Регистрация работодателя',
                           form=form, style=url_for('static', filename='css/style.css'))


@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    form = RegisterStudentForm()
    try:
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register_student.html', title='Регистрация студента',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="Passwords don't match")
            db_sess = db_session.create_session()
            if db_sess.query(Student).filter(Student.student_nsp == form.NSP.data,
                                             Student.born == form.born_date.data,
                                             Student.phone_num == form.phone_number.data).first():
                return render_template('register_student.html', title='Регистрация студента',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="This Student already exists")
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register_student.html', title='Регистрация студента',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="Account with this email already exists")
            if any(user.check_password(form.password.data) for user in db_sess.query(User).all()):
                return render_template('register_student.html', title='Регистрация студента',
                                       form=form, style=url_for('static', filename='css/style.css'),
                                       message="Account with this password already exists")

            if form.born_date.data.year < 1940:
                return render_template('register_student.html', title='Регистрация студента',
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
    except Exception as e:
        app.logger.error('An error occurred: %s', e)
        flash('Произошла неизвестная ошибка, попробуйте ещё раз', 'danger')
    return render_template('register_student.html', title='Регистрация студента',
                           form=form, style=url_for('static', filename='css/style.css'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    try:
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect('/workspace')
            return render_template('login.html', message="Wrong login or password",
                                   form=form, style=url_for('static', filename='css/style.css'), title='Вход')
    except Exception as e:
        app.logger.error('An error occurred: %s', e)
        flash('Произошла неизвестная ошибка, попробуйте ещё раз', 'danger')
    return render_template('login.html', title='Вход',
                           form=form, style=url_for('static', filename='css/style.css'))


@app.route('/university_workspace', methods=['POST', 'GET'])
@login_required
def university_workspace():
    try:
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        univer = user.university

        form_find = UniverFindStudentForm()
        form_open = UniverOpenCourseForm()
        form_close = UniverCloseCourseForm()

        all_acts = []
        student_find_table = ''
        projs = db_sess.query(Achievement).filter(Achievement.university_id == univer.id,
                                                  or_(Achievement.end_date == None,
                                                      Achievement.end_date == ""),
                                                  Achievement.approve_path == None
                                                  ).all()

        if form_find.validate_on_submit() and form_find.find_submit.data:
            student_id = str(form_find.find_student_id.data)
            if not student_id.isdigit():
                flash('ID студента, которого вы хотите найти, должен состоять только из цифр', "warning")
            else:
                student_id = int(student_id)
                student_find_table = db_sess.query(Student).filter(Student.id == student_id).first()
                if not student_find_table:
                    flash("Неверное ID студента для поиска", "warning")
                else:
                    all_acts = db_sess.query(Achievement).filter(
                        Achievement.student_id == student_id,
                        or_(Achievement.end_date == None,
                            Achievement.end_date == "")
                    ).all()
                    session['univer_found_student_id_cur'] = student_id

        if form_find.find_clear.data:
            session.pop('univer_found_student_id_cur', None)
            form_find.find_student_id.data = ''

        if form_open.validate_on_submit() and form_open.open_submit.data:
            student_id = str(form_open.open_student_id.data)
            if not student_id.isdigit():
                flash('ID студента, которому вы хотите открыть курс, должен состоять только из цифр', "warning")
            else:
                student_id = int(student_id)
                if db_sess.query(Student).get(student_id):
                    new_ach = Achievement(
                        title=str(form_open.open_course_title.data),
                        start_date=datetime.datetime.now(),
                        mark=random.choice([3, 4, 5]),
                        student_id=student_id,
                        university_id=univer.id,
                        approve_path='Not Required'
                    )
                    db_sess.add(new_ach)
                    db_sess.commit()
                    flash(f"Курс для студента с ID {student_id} открыт успешно, удачи!", "success")
                    return redirect(url_for('university_workspace'))
                else:
                    flash("Студент с таким ID не существует", "warning")

        if form_close.validate_on_submit() and form_close.close_submit.data:
            student_id = str(form_close.close_student_id.data)
            if not student_id.isdigit():
                flash('ID студента, которому вы хотите завершить курс, должен состоять только из цифр', "warning")
            else:
                student_id = int(student_id)
                got_title = form_close.close_course_title.data
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
                                             mark=found_course.mark,
                                             token=token)
                    found_course.file_path = file_path
                    db_sess.commit()
                    flash(f"Курс закрыт успешно, поздравляем! Токен: {token}.", "success")
                    return redirect(url_for('university_workspace'))
                else:
                    flash("Неверные данные для закрытия курса", "warning")

        if not student_find_table and 'univer_found_student_id_cur' in session:
            saved_id = session['univer_found_student_id_cur']
            student_find_table = db_sess.query(Student).get(saved_id)
            all_acts = db_sess.query(Achievement).filter(
                Achievement.student_id == saved_id,
                or_(Achievement.end_date == None,
                    Achievement.end_date == "")
            ).all()
            form_find.find_student_id.data = str(saved_id)

        return render_template('university_workspace.html',
                               form_find=form_find, form_close=form_close, form_open=form_open,
                               title='Образовательное учреждение',
                               student_find=student_find_table,
                               activities=all_acts,
                               projs=projs,
                               joined_title=univer.title,
                               style=url_for('static', filename='css/style.css'))
    except Exception as e:
        flash(f'Произошла неизвестная ошибка, попробуйте ещё раз', 'danger')
        app.logger.error(e)
        return render_template('home.html', token=None, result=None, university=None, title='Главная')


@app.route('/manage_proj', methods=["POST"])
@login_required
def manage_proj():
    try:
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
            mark = "approved"
            proj.approve_path = pdf_creating(student_nsp=proj.student.student_nsp,
                                             course_title=proj.title,
                                             univer_title=proj.university.title,
                                             start_date=proj.start_date,
                                             end_date=proj.end_date,
                                             univer_boss=proj.university.boss_nsp,
                                             token=proj.token,
                                             mark=mark,
                                             type="proj")
            proj.mark = mark
            db_sess.commit()
            flash("Проект подтверждён, сертификат подтверждения добавлен!", "success")

        return redirect(url_for('university_workspace'))
    except Exception as e:
        flash(f'Произошла неизвестная ошибка, попробуйте ещё раз', 'danger')
        app.logger.error(e)
        return render_template('home.html', token=None, result=None, university=None, title='Главная')


@app.route('/employer_workspace', methods=['GET', 'POST'])
@login_required
def employer_workspace():
    try:
        students = []
        achievements_data = []
        student_fullname = None
        form = EmplStudentSearchForm()

        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        employer = user.employer

        all_students = db_sess.query(Student).all()
        for student in all_students:
            cur_student_achs = db_sess.query(Achievement).filter(
                Achievement.student_id == student.id,
                Achievement.end_date.isnot(None),
                Achievement.end_date != ""
            ).all()
            if cur_student_achs:
                students.append({
                    'id': student.id,
                    'nsp': student.student_nsp,
                    'achievement_title': ', '.join([f'"{ach.title}"' for ach in cur_student_achs])
                })

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
                                'approve': a.approve_path,
                                'mark': a.mark
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
                               students=students,
                               achievements=achievements_data,
                               joined_title=employer.title,
                               entered_id="" if not form.student_id.data or form.clear.data else entered_student_id,
                               student_fullname=student_fullname,
                               style=url_for('static', filename='css/style.css'),
                               title='Работодатель')
    except Exception as e:
        flash(f'Произошла неизвестная ошибка, попробуйте ещё раз', 'danger')
        app.logger.error(e)
        return render_template('home.html', token=None, result=None, university=None, title='Главная')


@app.route('/student_workspace', methods=['GET', 'POST'])
@login_required
def student_workspace():
    try:
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        student = user.student
        form = UploadProjectForm()
        approved_achievements_data = []
        nonapproved_achievements_data = []
        active_courses_data = []
        inactive_courses_data = []
        employers_ids = []
        employers_data = []
        student_fullname = student.student_nsp.strip()

        univers = db_sess.query(University).all()
        form.univer_title.choices = [(u.title, u.title) for u in univers]
        if form.validate_on_submit():
            ach = form.file.data
            _, ext = os.path.splitext(form.file.data.filename)
            ach.save(os.path.join('static', 'achievements', f'{form.name.data}{ext}'))
            short_path = f'achievements/{form.name.data}{ext}'
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

        if student.employer_id:
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
                               student_id=student.id,
                               approved_achievements=approved_achievements_data,
                               nonapproved_achievements=nonapproved_achievements_data,
                               active_courses=active_courses_data,
                               inactive_courses=inactive_courses_data,
                               employers=employers_data,
                               style=url_for('static', filename='css/style.css'),
                               title='Студент')
    except Exception as e:
        flash(f'Произошла неизвестная ошибка, попробуйте ещё раз', 'danger')
        app.logger.error(e)
        return render_template('home.html', token=None, result=None, university=None, title='Главная')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    try:
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

            cur_pw = form.current_password.data
            new_pw = form.new_password.data
            if new_pw:
                if not cur_pw or not user.check_password(cur_pw):
                    flash('Текущий пароль введён неверно', 'danger')
                    return redirect(url_for('profile'))
                user.set_password(new_pw)
            try:
                db_sess.commit()
                flash('Профиль успешно обновлён', 'success')
            except Exception as e:
                db_sess.rollback()
                app.logger.error(e)
            return redirect(url_for('profile'))
        form.email.data = user.email

        return render_template('profile.html', form=form, role=user.role, title='Личный кабинет', user=user,
                               style=url_for('static', filename='css/style.css'), born=born)
    except Exception as e:
        flash(f'Произошла неизвестная ошибка, попробуйте ещё раз', 'danger')
        app.logger.error(e)
        return render_template('home.html', token=None, result=None, university=None, title='Главная')


@app.route("/check/certificate/<title>/<file_name>")
def certificate(title, file_name):
    try:
        workingdir = os.path.abspath(os.getcwd())
        filepath = workingdir + '/static/achievements/'
        return send_from_directory(filepath, file_name, download_name=f'certificate_{title}.pdf')
    except Exception as e:
        flash(f'Произошла неизвестная ошибка, попробуйте ещё раз', 'danger')
        app.logger.error(e)
        return render_template('home.html', token=None, result=None, university=None, title='Главная')


@app.route("/download/achievement/<title>/<filename>")
def download_ach(title, filename):
    try:
        db_sess = db_session.create_session()
        rel_path = f"achievements/{filename}"
        abs_path = os.path.join(app.root_path, 'static', rel_path)
        if not os.path.isfile(abs_path):
            abort(404)
        achievement = db_sess.query(Achievement).filter_by(file_path=rel_path).first()
        if not achievement or not achievement.student:
            abort(404)
        ext = os.path.splitext(abs_path)[1]
        download_name = f"{title}_{achievement.student.student_nsp}{ext}"

        return send_file(abs_path, as_attachment=True, download_name=download_name)
    except Exception as e:
        app.logger.error(e)


@app.route('/workspace')
@login_required
def workspace():
    try:
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
    except Exception as e:
        flash(f'Произошла неизвестная ошибка, попробуйте ещё раз', 'danger')
        app.logger.error(e)
        return render_template('home.html', token=None, result=None, university=None, title='Главная')


def main():
    try:
        db_session.global_init("db/EduCred_data.db")
        port = int(os.environ.get("PORT", 8000))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        app.logger.error(e)


if __name__ == '__main__':
    main()

    # My web: https://precious-fluoridated-muskox.glitch.me/
    # create git with only this directory on git. just files of that github
    # My Projects: https://glitch.com/dashboard?group=owned&sortColumn=boost&sortDirection=DESC&page=1&showAll=false&filterDomain=
