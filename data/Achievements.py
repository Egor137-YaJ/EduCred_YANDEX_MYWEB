import datetime
import uuid
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


# модель таблицы достижений из бд
class Achievement(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "achievements"

    # настройка полей таблицы
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    token = sqlalchemy.Column(sqlalchemy.String(64), nullable=True, unique=True)
    approve_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    file_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.now())
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    mark = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("students.id"))
    university_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("universities.id"))

    # настройка связей таблицы
    student = orm.relationship("Student", back_populates="achievements")
    university = orm.relationship("University", back_populates="achievements")
