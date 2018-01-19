from ..extensions import db

class TagsModel(db.Model):
    __tablename__ = 'tags'
    tid = db.Column('tid', db.String(12), primary_key=True)
    name = db.Column('name', db.String(128))
