from db_api.extensions import db
from sqlalchemy.types import String
from sqlalchemy.schema import Column

class CategoryModel(db.Model):
    __tablename__ = 'category'
    tid = Column('cid', db.String(12), primary_key=True)
    name = Column('name', db.String(128))