from ..extensions import db
from .TagsNotesTable import TagsNotesTable

class NotesModel(db.Model):
    __tablename__ = 'notes'
    nid = db.Column('nid', db.String(12), primary_key=True)
    name = db.Column('name', db.String(128))
    owner = db.Column('owner_uid', db.String(128))
    hash = db.Column('hash', db.String(128))
    creation_date = db.Column(db.DateTime)
    update_date = db.Column(db.DateTime)
    path = db.Column(db.String(128))
    tags = db.relationship('TagsModel', secondary=TagsNotesTable, lazy='subquery',
           backref=db.backref('tagsnotes', lazy=True))
