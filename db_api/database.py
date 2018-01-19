from db_api.common.utils import ConversionUtils, IDTools

class AppuntiDB():

    def __init__(self, database, users_model, notes_model, tags_model):
        self.db = database
        self.UsersModel = users_model.UsersModel
        self.NotesModel = notes_model.NotesModel
        self.TagsModel  = tags_model.TagsModel
        self.IDTools = IDTools(self.UsersModel, self.NotesModel, self.TagsModel)
        self.ConversionUtils = ConversionUtils(self.UsersModel,
                                               self.NotesModel,
                                               self.TagsModel)

    def all_users(self):
        all = self.UsersModel.query.all()
        return list(map(self.ConversionUtils.User_Model2Dict, all))

    def add_user(self, username, mail=None):
        new_uid = self.IDTools.get_new_ID()
        new_user = {
            'type':     'user',
            'UID':      new_uid,
            'username': username,
            'mail':     mail
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
            'type':  'note',
            'NID':   new_nid,
            'name':  name,
            'owner': owner,
            'hash':  None,
            'path':  None
        }
        new_note = self.ConversionUtils.Note_Dict2Model(new_note)
        for tag in tags:
            tag_obj = self.add_tag(tag)
            new_note.tags.append(tag_obj)
        self.db.session.add(new_note)
        self.db.session.commit()
        return new_nid

    # def add_note_tags(self, nid, tags=[]):
    #     note = self.NotesModel.query.filter_by(nid=nid)
    #     note.tags.append(tags)
    #     self.db.session.add(note)
    #     self.db.session.commit()

    def add_note_file(self, nid, file):
        hash = sha256(file)
        s3_path = 'appunti_main_bucket/' + hash + '.' + new_nid
        s3_hash = upload_file(s3_path, file)
        if (hash != s3_hash):
            abort(404)  #### ADD CORRECT CODE
        notes_json[nid]['hash'] = hash
        notes_json[nid]['path'] = s3_path


    def get_note(self, nid):
        abort_if_note_doesnt_exist(nid)
        note = self.NotesModel.query.filter_by(nid=nid)
        return self.ConversionUtils.Note_Model2Dict(note)

    def del_note(self, nid):
        note = self.NotesModel.query.filter_by(nid=nid)
        self.db.session.delete(note)
        self.db.session.commit()
        return note.nid

    def update_note(self, nid, name=None, owner=None, tags=None):
        if name == None and owner == None and tags == None:
            return None
        if name != None:
            notes_json[nid]['name'] = name
        if owner != None:
            notes_json[nid]['owner'] = owner
        if tags != None:
            notes_json[nid]['tags'] = tags
        return nid

    def add_tag(self, name, return_object=True):
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

    def search(self, query, tags, uid):
        if query == None:
            return None
        ### Fiters stuff

        #if self.IDTools.user_exist(uid):
        #    matches = self.UsersModel.query.filter_by(uid=uid)
        #if type(tags) == list:
        #    for tag in tags:
        #        matches.
        q = self.NotesModel.query

        print('search method inside AppuntiDB')
        print('query: {}\ntags: {}\nuid: {}'.format(query, tags, uid))

        if self.IDTools.user_exist(uid):
            q = q.filter_by(owner = uid)
        else:
            return None

        if type(tags) is list:
            q = q.join(self.TagsModel, self.NotesModel.tags)
            for tag in tags:
                q = q.filter(self.NotesModel.tags.any(self.TagsModel.name == tag))
        if query != None and query != '':
            q = q.filter(self.NotesModel.name.contains(query))

        #q = (self.NotesModel.query
        #     .filter_by(owner=uid)
        #     .join(self.TagsModel, self.NotesModel.tags)
        #     .filter(self.NotesModel.tags.any(self.TagsModel.name==tags[0]))
        #     .filter(self.NotesModel.name.contains(query)))

        return [self.ConversionUtils.Note_Model2Dict(note) for note in q.all()]

        #q = (NotesModel.query
        #     .filter_by(owner=uid)
        #     .filter(Notes.tags.any(TagsModel.name == tags))
        #     .filter(Notes.tags.any(TagsModel.name == tags
