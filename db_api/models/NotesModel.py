from db_api.extensions import db
from db_api.models.TagsNotesTable import TagsNotesTable
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import DateTime, String, Integer
from sqlalchemy.schema import Column
from sqlalchemy.orm import backref, relationship


class NotesModel(db.Model):
    __tablename__ = 'notes'
    nid = Column('nid', String(12), primary_key=True)
    name = Column('name', String(128))
    owner = Column('owner_uid', String(128))
    creation_date = Column(DateTime)
    update_date = Column(DateTime)
    path = Column(postgresql.ARRAY(String(128), dimensions=1))
    pages = Column(Integer())
    tags = relationship('TagsModel', secondary=TagsNotesTable, lazy='subquery',
           backref=backref('tagsnotes', lazy=True))