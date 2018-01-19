from ..extensions import db

TagsNotesTable = db.Table('tagsnotes',
                    db.Column('tid', db.String(12),
                              db.ForeignKey('tags.tid'), primary_key=True),
                    db.Column('nid', db.String(12),
                              db.ForeignKey('notes.nid'), primary_key=True)
                    )
