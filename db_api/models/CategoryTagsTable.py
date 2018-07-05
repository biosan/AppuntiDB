from db_api.extensions import db, Base
from sqlalchemy.types import String
from sqlalchemy.schema import Column, Table, ForeignKey

CategoryTagsTable = Table('categorytags',
                          Base.metadata,
                          Column('cid', String(12),
                              ForeignKey('category.cid'),
                              primary_key=True),
                          Column('tid', String(12),
                              ForeignKey('tags.tid'),
                              primary_key=True)
                         )