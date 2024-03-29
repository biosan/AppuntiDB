from db_api.common.utils  import ConversionUtils, IDTools, HashStuff
from db_api.cloud_storage import B2
import hashlib, base64
from passlib.hash import argon2
from functools import reduce
from db_api.extensions import logger, auth

import sys


def abort(code):
    pass

class AppuntiDB():

    def __init__(self, database, users_model, notes_model,
                 tags_model, category_model, b2_dict):
        self.db = database
        self.UsersModel = users_model.UsersModel
        self.NotesModel = notes_model.NotesModel
        self.TagsModel  = tags_model.TagsModel
        self.CategoryModel = category_model.CategoryModel
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


    ###
    ### Search
    ###

    def search2(self, query='', tags=[], uid=None, category={}):
        output_list = lambda q: [self.ConversionUtils.Note_Model2Dict(note) for note in q.all()]
        q = self.NotesModel.query
        if uid != None and self.IDTools.user_exist(uid):
            q = q.filter(self.NotesModel.owner == uid)
        if query != '' and query != None:
            q = q.filter(self.NotesModel.name.ilike('%'+query+'%'))
        if q.count() == 0:
            return output_list(q)
        q = q.join(self.TagsModel, self.NotesModel.tags)
        q = q.join(self.CategoryModel, self.TagsModel.category)
        for tag in tags:
            q = q.filter(self.NotesModel.tags.any(self.TagsModel.name == tag))



    def search(self, query='', tags=[], uid=None, category={}):

        if query == None:
            query = ''

        q = self.NotesModel.query

        if uid != None and self.IDTools.user_exist(uid):
            q = q.filter_by(owner = uid)

        ### TODO: Search in categories
        #if type(category) is dict and len(category)>0:
        #   for cat, value in category:
        #       q = q.filter(self.NotesModel.tags.any(self.TagsModel.name == tag))
        #
        # - Check if category is a valid dictionary
        # - Filter category dictionary by allowed categories
        # - For every k,v pair in category filter the query
        #   - How to filter?
        #   - For every tag search if it has category 'cat'
        #   - If yes then compare and add to query
        #   - If yes then 
        #
        #####################
        # 1. Cercare tag con categoria adatta
        category_tags_tid = []
        if type(category) is dict and len(category)>0:
            for cat, value in category.items():
                """
                category_model_item = self.CategoryModel.query.filter(self.CategoryModel.name == cat).first()
                if category_model_item == None:
                    break
                tag_model_item = self.TagsModel.query.filter(self.TagsModel.name == value)
                tag_model_item = tag_model_item.join(self.CategoryModel, self.TagsModel.category).filter(self.TagsModel.category.any(self.CategoryModel.cid == category_model_item.cid)).first()
                if tag_model_item == None:
                    break
                category_tags_tid.append(tag_model_item.tid)
                """
                tag_model_item= self.db.session.query(self.TagsModel).join(self.CategoryModel, self.TagsModel.category)\
                                              .filter(self.TagsModel.name == value)\
                                              .filter(self.CategoryModel.name == cat).first()
                if tag_model_item == None:
                    break
                category_tags_tid.append(tag_model_item.tid)
                ### TODO: It could work?
                ###category_tags_tid = [t.tid for t in self.TagsModel if t.category.name == cat and t.name == value]


        #####################
        if type(tags) is list:
            q = q.join(self.TagsModel, self.NotesModel.tags)
            tags = tuple(map(str.lower, tags))
            ### TODO: To delete when category search is completed
            tags = tags + tuple(category.values())
            for tag in tags:
                q = q.filter(self.NotesModel.tags.any(self.TagsModel.name == tag))

        for tid in category_tags_tid:
            q = q.filter(self.NotesModel.tags.any(self.TagsModel.tid == tid))

        if query != '':
            q = q.filter(self.NotesModel.name.contains(query))

        output = [self.ConversionUtils.Note_Model2Dict(note) for note in q.all()]
        logger.debug('AppuntiDB.search (query={}, tags={}, uid={}) => output:{}'.format(query, tags, uid, output))
        return output



    ###
    ### Users stuff
    ###
    def all_users(self):
        all = self.UsersModel.query.all()
        return list(map(self.ConversionUtils.User_Model2Dict, all))


    def add_user(self, username, password, mail=None):
        new_uid = self.IDTools.get_new_ID()
        new_user = {
        'type':     'user',
        'uid':      str(new_uid),
        'username': str(username),
        'mail':     str(mail)
        }
        new_user_model = self.ConversionUtils.User_Dict2Model(new_user)
        new_user_model.password = argon2.hash(str(password))
        self.db.session.add(new_user_model)
        self.db.session.commit()
        logger.debug('Added new user: {}'.format(new_user))
        return new_uid


    def get_user(self, uid):
        user = self.UsersModel.query.filter_by(uid=uid).first()
        return self.ConversionUtils.User_Model2Dict(user)


    def update_user(self, uid, username=None, mail=None, password=None):
        update = False
        if self.IDTools.user_exist(uid):
            user = self.UsersModel.query.filter_by(uid=uid).first()
            new_user = self.get_user(uid)
            new_user['password'] = user.password
        else:
            abort(404)

        if (username != None and not self.IDTools.username_exist(username)):
            new_user['username'] = username
            update = True
        if (mail != None and not self.IDTools.mail_exist(mail)):
            new_user['mail'] = mail
            update = True
        if (password != None):
            new_user['password'] = argon2.hash(password)
            update = True

        if update:
            user.username = new_user['username']
            user.mail = new_user['mail']
            user.password = new_user['password']
            self.db.session.commit()
            logger.debug('Updated user: {}'.format(new_user))
        logger.debug('User not updated: {}'.format(new_user))


    def del_user(self, uid):
        user = self.UsersModel.query.filter_by(uid=uid).first()
        self.db.session.delete(user)
        self.db.session.commit()
        logger.debug('User deleted: {}'.format(user))
        return user.uid


    def authenticate_user(self, anyID, password):
        uid = self.ConversionUtils.toUID(anyID)
        user = self.UsersModel.query.filter_by(uid=uid).first()
        if (user == None):
            return False
        return argon2.verify(password, user.password)



    ###
    ### Notes stuff
    ###
    def all_notes(self):
        notes = self.NotesModel.query.all()
        return list(map(self.ConversionUtils.Note_Model2Dict, notes))


    def add_note(self, name, owner, tags=[], category_tags={}):
        new_nid = self.IDTools.get_new_ID()
        new_note = {
            'type' : 'note',
            'nid'  : new_nid,
            'name' : name,
            'owner': owner,
            'path' : None,
            'pages': None
        }
        new_note = self.ConversionUtils.Note_Dict2Model(new_note)
        if type(tags) != list:
            tags = []
        if type(category_tags) != dict:
            category_tags = {}
        for tag in tags:
            tag_obj = self.add_tag(tag)
            new_note.tags.append(tag_obj)
            print('tags: {}'.format(tag), file=sys.stderr)
        for category, tag in category_tags.items():
            tag_obj = self.add_tag(tag, category)
            new_note.tags.append(tag_obj)
            print('cat tags: {}:{}'.format(category, tag), file=sys.stderr)
        self.db.session.add(new_note)
        self.db.session.commit()
        logger.critical('Added new note: {}'.format(new_note))
        print('Added new note: {}'.format(new_note), file=sys.stderr)
        return new_nid


    def get_note(self, nid):
        note = self.NotesModel.query.filter_by(nid=nid).first()
        return self.ConversionUtils.Note_Model2Dict(note)


    def del_note(self, nid):
        note = self.NotesModel.query.filter_by(nid=nid).first()
        self.db.session.delete(note)
        self.db.session.commit()
        logger.debug('Deleted note: {}'.format(note))
        return note.nid


    def update_note(self, nid, name=None, owner=None, tags=None, category=None):
        update = False
        update_tags = False
        if self.IDTools.note_exist(nid):
            note = self.NotesModel.query.filter_by(nid=nid).first()
            new_note = self.get_note(nid)
        else:
            abort(404)

        if (name != None):
            new_note['name'] = name
            update = True
        if (owner != None and self.IDTools.user_exist(owner)):
            new_note['owner'] = owner
            update = True
        if (tags != None):
            if type(tags) != list:
                tags = list(tags)
            for tag in tags:
                note.tags.append(self.add_tag(tag))
            update_tags = True
        if (category != None and type(category) == dict):
            for c, n in category.items():
                note.tags.append(self.add_tag(n, category_name=c))
            update_tags = True

        if update or update_tags:
            note.name = new_note['name']
            note.owner = new_note['owner']
            self.db.session.commit()
            logger.debug('Note updated: {}'.format(new_note))
        logger.debug('Note not updated: {}'.format(new_note))



    ###
    ### Notes files stuff
    ###
    def get_note_file(self, nid, page=None):
        if self.IDTools.note_exist(nid):
            note = self.get_note(nid)
        else:
            abort(404)
        files = []
        if page==None:
            for page_path in note['path']:
                files.append(self.b2.download(name = page_path))
        elif (0 <= page < note['pages'] and type(note['path']) is list and len(note['path'])>0):
            files = self.b2.download(name = note['path'][page])
        else:
            abort(404)
        return files


    def add_note_files(self, nid, files):
        if self.IDTools.note_exist(nid):
            note_model = self.NotesModel.query.filter_by(nid=nid).first()
        else:
            return None
        if type(files) != list:
            files = list(files)
        ###LOGGING###print('add_note_file x: ', files, file=sys.stderr)
        files_hash_list = HashStuff.hash_func(files)
        for i, file in enumerate(files):
            self.b2.upload(file, name = files_hash_list[i])
        note_model.path = files_hash_list
        note_model.pages = len(files)
        self.db.session.commit()


    def delete_note_files(self, nid, pages):
        if self.IDTools.note_exist(nid):
            note = self.get_note(nid)
            note_model = self.NotesModel.query.filter_by(nid=nid).first()
        else:
            abort(404)  ### ADD CORRECT CODE
        is_valid_index = lambda x: 0 <= x < note['pages']
        to_delete = []
        if type(pages) is list:
            to_delete = list(map(is_valid_index, pages))
        if type(pages) is str:
            if pages.to_lower == 'all':
                to_delete = list(range(0, note['pages']))
        if type(pages) is int:
            if is_valid_index(pages):
                to_delete.append(pages)
        paths = note['path']
        for p, i in enumerate(pages):
            self.b2.delete(paths[i])
            paths.remove(i)
        note_model.path  = paths
        note_model.pages = len(paths)
        self.db.session.commit()


    def append_note_files(self, nid, files):
        if self.IDTools.note_exist(nid):
            note = self.get_note(nid)
            note_model = self.NotesModel.query.filter_by(nid=nid).first()
        else:
            abort(404)  ### ADD CORRECT CODE
        if type(files) != list:
            files = list(files)
        files_hash_list = HashStuff.hash_func(files)
        new_paths = note['path'].copy()
        for i, file in enumerate(files):
            self.b2.upload(file, name = files_hash_list[i])
            new_paths.append(files_hash_list[i])
        note_model.path  = new_paths
        note_model.pages = len(new_paths)
        self.db.session.commit()



    ###
    ### Tags stuff
    ###
    def add_tag(self, name, category_name=None, return_object=True):
        name = name.lower()
        tag = self.TagsModel.query.filter_by(name=name).first()
        if tag != None:
            if tag.name == name:
                if return_object:
                    return tag
                else:
                    return tag.tid

        new_tid = self.IDTools.get_new_ID()
        new_tag = self.TagsModel(tid = new_tid, name = name)

        if category_name != None:
            category = self.CategoryModel.query.filter_by(name=category_name).first()
            if category != None:
                new_tag.category = [category]

        self.db.session.add(new_tag)
        self.db.session.commit()

        if return_object:
            return new_tag
        else:
            return new_tid


    def add_tag_json(self, tag_json, return_object=True):
        pass
