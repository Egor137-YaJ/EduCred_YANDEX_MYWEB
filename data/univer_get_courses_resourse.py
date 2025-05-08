from flask_restful import Resource
from flask import request, jsonify
from flask_login import login_required
from data import db_session
from data.Achievements import Achievement

class StudentCoursesAPI(Resource):
    method_decorators = [login_required]

    def get(self):
        student_id = request.args.get('student_id')

        if not student_id or not student_id.isdigit():
            return jsonify([])

        db_sess = db_session.create_session()
        achievements = db_sess.query(Achievement).filter(
            Achievement.student_id == int(student_id),
            Achievement.start_date != None,
            Achievement.end_date == None
        ).all()

        titles = [a.title for a in achievements]
        return jsonify(titles)