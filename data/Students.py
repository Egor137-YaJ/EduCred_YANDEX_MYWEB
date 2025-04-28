import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Student(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "students"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    student_nsp = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    born = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    phone_num = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    employer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("employers.id"))

    user = orm.relationship("User", back_populates="student")
    employer = orm.relationship("Employer", back_populates="students")
    achievements = orm.relationship("Achievement", back_populates="student")