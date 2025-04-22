import datetime
import uuid
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Achievement(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "achievements"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    token = sqlalchemy.Column(sqlalchemy.String(64), nullable=False, unique=True, default=lambda: str(uuid.uuid4()))
    file_path = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.now())
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("students.id"))
    university_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("universities.id"))

    ...