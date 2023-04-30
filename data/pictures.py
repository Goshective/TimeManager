import sqlalchemy

from .db_session import SqlAlchemyBase


class Pictures(SqlAlchemyBase):
    __tablename__ = 'pictures'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                sqlalchemy.ForeignKey("users.id"), unique=True)
    data = sqlalchemy.Column(sqlalchemy.LargeBinary)
    
    user = sqlalchemy.orm.relationship('User', uselist=False, back_populates='picture')