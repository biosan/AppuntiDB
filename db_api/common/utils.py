from base64 import urlsafe_b64encode, urlsafe_b64decode
from random import getrandbits

########################
### Conversion Utils ###
########################

class ConversionUtils():
    def __init__(self, users_model, notes_model, tags_model):
        self.UsersModel = users_model
        self.NotesModel = notes_model
        self.TagsModel = tags_model

    def User_Model2Dict(self, user_model):
        user = {
            'type':     'user',
            'UID':      user_model.uid,
            'username': user_model.username,
            'mail':     user_model.mail
        }
        return user

    def User_Dict2Model(self, user_dict):
        user = self.UsersModel(uid      = user_dict['UID'],
                          username = user_dict['username'],
                          mail     = user_dict['mail'])
        return user


    def Note_Model2Dict(self, note_model):
        note = {
            'type':  'note',
            'NID':   note_model.nid,
            'name':  note_model.name,
            'owner': note_model.owner,
            'hash':  note_model.hash,
            'tags':  [],
            'path':  note_model.path
        }
        for tag in note_model.tags:
            note['tags'].append(tag.name)
        return note

    def Note_Dict2Model(self, note_dict):
        note = self.NotesModel(nid = note_dict['NID'],
                          name = note_dict['name'],
                          owner = note_dict['owner'],
                          hash = note_dict['hash'],
                          path = note_dict['path'])
        #for tag in note_dict['tags']:
        #    note.tags.append(tag)
        return note


#################
### IDs Tools ###
#################

class IDTools():
    def __init__(self, users_model, notes_model, tags_model):
        self.UsersModel = users_model
        self.NotesModel = notes_model
        self.TagsModel  = tags_model

    def user_exist(self, uid):
        return self.UsersModel.query.filter_by(uid=uid).first() != None

    def note_exist(self, nid):
        return self.NotesModel.query.filter_by(nid=nid).first() != None

    def tag_exist(self, tid):
        return self.TagsModel.query.filter_by(tid=tid).first() != None

    def generate(self):
        return urlsafe_b64encode(bytes((getrandbits(8) for i in range(8))))

    def get_new_ID(self):
        id = ''
        while (id == '' or self.user_exist(id) or self.note_exist(id)) or self.tag_exist(id):
            id = self.generate()
        return str(id)[2:-1]
