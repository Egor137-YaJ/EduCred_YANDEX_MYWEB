import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Employer(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "employers"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    INN = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    boss_nsp = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    phone_num = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    scope = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user = orm.relationship("User", back_populates="employer")
    students = orm.relationship("Student", back_populates="employer")