import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


# модель таблицы с данными о юзерах
class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "users"

    # настройка полей таблицы
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    role = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    # настройка связей таблицы
    university = orm.relationship("University", back_populates="user", uselist=False)
    employer = orm.relationship("Employer", back_populates="user", uselist=False)
    student = orm.relationship("Student", back_populates="user", uselist=False)

    # функции для смены и хеширования пароля
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
