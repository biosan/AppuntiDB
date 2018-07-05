from db_api.extensions import db
from db_api.models.CategoryTagsTable import CategoryTagsTable
from sqlalchemy.types import String
from sqlalchemy.schema import Column
from sqlalchemy.orm import backref, relationship

class TagsModel(db.Model):
    __tablename__ = 'tags'
    tid = Column('tid', String(12), primary_key=True)
    name = Column('name', String(128))
    category = relationship('CategoryModel', secondary=CategoryTagsTable, lazy='subquery',
                               backref=backref('categorytags', lazy=True))