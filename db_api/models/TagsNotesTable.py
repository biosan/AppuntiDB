from db_api.extensions import db, Base
from sqlalchemy.types import String
from sqlalchemy.schema import Column, Table, ForeignKey

TagsNotesTable = Table('tagsnotes',
                       Base.metadata,
                       Column('tid', String(12), ForeignKey('tags.tid'), primary_key=True),
                       Column('nid', String(12), ForeignKey('notes.nid'), primary_key=True)
                       )