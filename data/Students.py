import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


# модель таблицы с данными о студентах
class Student(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "students"

    # настройка полей таблицы
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    student_nsp = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    born = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    phone_num = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    employer_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    # настройка связей таблицы
    user = orm.relationship("User", back_populates="student")
    achievements = orm.relationship("Achievement", back_populates="student")