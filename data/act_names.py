import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Activities_names(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'activities_names'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                sqlalchemy.ForeignKey("users.id"))
    # category
    recs = orm.relationship("Records", back_populates='act_n')
    user = orm.relationship("User", back_populates='act_names')