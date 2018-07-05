from db_api.extensions import logger
from base64 import urlsafe_b64encode, urlsafe_b64decode
import random
import secrets


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
        user = self.UsersModel(uid = user_dict['uid'],
                          username = user_dict['username'],
                          mail     = user_dict['mail'])
        return user


    def Note_Model2Dict(self, note_model):
        note = {
            'type':  'note',
            'nid':   note_model.nid,
            'name':  note_model.name,
            'owner': note_model.owner,
            'tags':  [],
            'path':  note_model.path,
            'pages': note_model.pages
        }
        for tag in note_model.tags:
            #print(tag.category, file=sys.stderr)
            if len(tag.category) > 0:
                #print(tag.category[0].name, tag.name, file=sys.stderr)
                note[tag.category[0].name] = tag.name
            else:
                note['tags'].append(tag.name)
            
        return note

    def Note_Dict2Model(self, note_dict):
        note = self.NotesModel(nid = note_dict['nid'],
                          name = note_dict['name'],
                          owner = note_dict['owner'],
                          path = note_dict['path'],
                          pages = note_dict['pages'])
        #for tag in note_dict['tags']:
        #    note.tags.append(tag)
        return note
    
    #def Tag_Dict2Model(self, tag_dict):
    #    tag = self.TagsModel(tid = tag_dict['tid'],
    #                         name = tag_dict['name'])
    #    pass

    def toUID(self, anyID):
        query  = self.UsersModel.query.filter_by(uid      = anyID).all()
        query += self.UsersModel.query.filter_by(username = anyID).all()
        query += self.UsersModel.query.filter_by(mail     = anyID).all()
        logger.critical("query: {}".format(query))
        if (len(query) >= 1):
            return query[0].uid
        else:
            return None
    
    def toUsername(self, uid):
        query = self.UsersModel.query.filter_by(uid=uid).first()
        if query != None:
            return query.username
        return None


##################
### Tags Tools ###
##################
class TagsTools():
    def __get_category(self, tag):
        pass

    def __set_category(self, s1, s2):
        #return s1 + ':' + s2
        pass

    def get_category(self, tag):
        if type(tag) is str:
            return self.__get_category(tag)[0]
        if type(tag) is list:
            return [self.__get_category(t)[0] for t in tag]

    def set_category(self, tag, category):
        if type(category) is str:
            if type(tag) is str:
                return self.__set_category(category, tag)
            if type(tag) is list:
                for t in tag:
                    self.__set_category(category, t)


#################
### IDs Tools ###
#################

class IDTools():
    def __init__(self, users_model, notes_model, tags_model):
        self.UsersModel = users_model
        self.NotesModel = notes_model
        self.TagsModel  = tags_model

    def user_exist(self, uid):
        users = self.UsersModel.query.filter_by(uid=uid).first()
        print('This are the users: ', users)
        exist = users != None
        return exist

    def note_exist(self, nid):
        return self.NotesModel.query.filter_by(nid=nid).first() != None

    def tag_exist(self, tid):
        return self.TagsModel.query.filter_by(tid=tid).first() != None
    
    def username_exist(self, username):
        pass
    
    def mail_exist(self, mail):
        pass

    # def generate(self):
    #     return str(urlsafe_b64encode(bytes((getrandbits(8) for i in range(8)))))[2:1]

    def generate(self):
        return secrets.token_urlsafe(8)

    def get_new_ID(self):
        #id = ''
        #while (id == '' or self.user_exist(id) or self.note_exist(id) or self.tag_exist(id)):
        #    id = self.generate()
        #return id #str(id)[2:-1]

        ids = [self.generate() for i in range(2)]
        id_not_exists = lambda id: not (self.user_exist(id) or self.note_exist(id) or self.tag_exist(id))
        uniques = tuple(filter(id_not_exists, ids))
        if len(uniques) == 0:
            print('Double collision. IDs:', ids)
            return None
        else:
            return uniques[0]