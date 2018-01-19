from ..extensions import db

class UsersModel(db.Model):
    __tablename__ = 'users'
    uid = db.Column('uid', db.String(12), primary_key=True)
    username = db.Column('username', db.String(128))
    mail = db.Column('mail', db.String(128))
    creation_date = db.Column(db.DateTime)
