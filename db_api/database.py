from db_api.common.utils  import ConversionUtils, IDTools
from db_api.cloud_storage import B2
import hashlib, operator, base64
from functools import reduce

class AppuntiDB():

    def __init__(self, database, users_model, notes_model, tags_model, b2_dict):
        self.db = database
        self.UsersModel = users_model.UsersModel
        self.NotesModel = notes_model.NotesModel
        self.TagsModel  = tags_model.TagsModel
        self.IDTools = IDTools(self.UsersModel, self.NotesModel, self.TagsModel)
        self.ConversionUtils = ConversionUtils(self.UsersModel,
                                               self.NotesModel,
                                               self.TagsModel)
        self.b2 = B2(account_id      = b2_dict['account_id'],
                     application_key = b2_dict['application_key'],
                     bucket_id       = b2_dict['bucket_id'],
                     bucket_name     = b2_dict['bucket_name'])
        self.userID_to_SID = dict()
        self.ws_clients = dict()

    def all_users(self):
        all = self.UsersModel.query.all()
        return list(map(self.ConversionUtils.User_Model2Dict, all))

    def add_user(self, username, mail=None):
        new_uid = self.IDTools.get_new_ID()
        new_user = {
            'type':     'user',
            'UID':      str(new_uid),
            'username': str(username),
            'mail':     str(mail)
            }
        new_user = self.ConversionUtils.User_Dict2Model(new_user)
        self.db.session.add(new_user)
        self.db.session.commit()
        return new_uid

    def get_user(self, uid):
        user = self.UsersModel.query.filter_by(uid=uid).first()
        return self.ConversionUtils.User_Model2Dict(user)

    def update_user(self, uid, username=None, mail=None):
        if username == None and mail == None:
            return None

        user = self.UsersModel.query.filter_by(uid=uid).first()
        ###TODO### # How to update entry?
        if username != None:
            users_json[uid]['username'] = username
        if owner != None:
            users_json[uid]['mail'] = mail
        return uid


    def del_user(self, uid):
        user = self.UsersModel.query.filter_by(uid=uid).first()
        self.db.session.delete(user)
        self.db.session.commit()
        return user.uid


    def all_notes(self):
        notes = self.NotesModel.query.all()
        return list(map(self.ConversionUtils.Note_Model2Dict, notes))

    def add_note(self, name, owner, tags=[]):
        new_nid = self.IDTools.get_new_ID()
        new_note = {
            'type' : 'note',
            'NID'  : new_nid,
            'name' : name,
            'owner': owner,
            'hash' : None,
            'path' : None,
            'pages': None
        }
        new_note = self.ConversionUtils.Note_Dict2Model(new_note)
        for tag in tags:
            tag_obj = self.add_tag(tag)
            new_note.tags.append(tag_obj)
        self.db.session.add(new_note)
        self.db.session.commit()
        return new_nid

    def add_note_files(self, nid, files):
        if self.IDTools.note_exist(nid):
            note = self.NotesModel.query.filter_by(nid=nid).first()
        else:
            abort(404)  ### ADD CORRECT CODE
        hash = self.__multi_file_hash(files)
        if len(files) > 1:
            for part, file in enumerate(files):
                self.b2.upload(file, nid, hash, part)
        else:
            self.b2.upload(files[0], nid, hash)
        note.path = self.b2.get_path(nid, hash)  ### TODO: Which path when file has more than one part/page?
        note.hash = hash
        note.pages = len(files)
        self.db.session.commit()

    def append_note_files(self, nid, files):
        if self.IDTools.note_exist(nid):
            note = self.get_note(nid)
        else:
            abort(404)  ### ADD CORRECT CODE
        ### TODO
        ### PROBLEM: How to update hash on DB and on filename - How to update part number if no previous parts exists?
        ### Sol1: Hashing: - Combine single file hash with xor
        ###                - Use BLAKE2 incremental hashing
        ###                (Still have to update filenames or maybe use a folder...)
        if len(files) > 1:
            for part, file in enumerate(files):
                self.b2.upload(file, nid, hash, part)
        else:
            self.b2.upload(files[0], nid, hash)


    def get_note_file(self, nid, page=None):
        if not self.IDTools.note_exist(nid):
            abort(404)
        note = self.NotesModel.query.filter_by(nid=nid).first()
        files = []
        if page==None:
            for page_index in range(note.pages):
                files.append(self.b2.download(nid, note.hash, page_index))
            return files
        return self.b2.download(nid, note.hash, page)

    ### Add to common utils
    def sha256(self, x):
        return hashlib.sha256(bytes(x)).digest()

    def xor_bytes(self, a, b):
        return bytes(map(operator.xor, a, b))

    def __multi_file_hash(self, files):
        out = base64.b16encode(reduce(self.xor_bytes, map(self.sha256, files)))
        out = str(out)[2:-1]
        print(out)
        return out

    def get_note(self, nid):
        note = self.NotesModel.query.filter_by(nid=nid).first()
        return self.ConversionUtils.Note_Model2Dict(note)

    def del_note(self, nid):
        note = self.NotesModel.query.filter_by(nid=nid).first()
        self.db.session.delete(note)
        self.db.session.commit()
        return note.nid

    def update_note(self, nid, name=None, owner=None, tags=None):
        if name == None and owner == None and tags == None:
            return None

        note = self.NotesModel.query.filter_by(nid=nid)
        if name != None:
            note.name = name
        if owner != None and self.IDTools.user_exist(owner):
            note.owner = owner
        if tags != None:
            for tag in tags:
                tag_obj = self.add_tag(tag)
                new_note.tags.append(tag_obj)
        self.db.commit()
        return self.ConversionUtils.Note_Model2Dict(note)

    def add_tag(self, name, return_object=True):
        name = name.lower()
        tag = self.TagsModel.query.filter_by(name=name).first()
        if tag != None:
            if tag.name == name:
                if return_object:
                    return tag
                else:
                    return tid
        new_tid = self.IDTools.get_new_ID()
        new_tag = self.TagsModel(tid = new_tid, name = name)
        self.db.session.add(new_tag)
        self.db.session.commit()
        if return_object:
            return new_tag
        else:
            return new_tid

    def search(self, query, tags=[], uid=None):
        if query == None:
            return None

        q = self.NotesModel.query

        if uid != None and self.IDTools.user_exist(uid):
            q = q.filter_by(owner = uid)
        if type(tags) is list:
            q = q.join(self.TagsModel, self.NotesModel.tags)
            tags = tuple(map(str.lower, tags))
            for tag in tags:
                q = q.filter(self.NotesModel.tags.any(self.TagsModel.name == tag))
        if query != None and query != '':
            q = q.filter(self.NotesModel.name.contains(query))

        return [self.ConversionUtils.Note_Model2Dict(note) for note in q.all()]
