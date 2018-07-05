from db_api.extensions import db
from sqlalchemy.types import DateTime, String
from sqlalchemy.schema import Column

class UsersModel(db.Model):
    __tablename__ = 'users'
    uid = Column('uid', String(12), primary_key=True)
    username = Column('username', String(128))
    mail = Column('mail', String(128))
    password = Column('password', String(128))
    creation_date = Column(DateTime)