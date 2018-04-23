#from gevent import monkey
#monkey.patch_all() 
import os
from flask import Flask
from flask_restful import Api

import db_api.config as     Config
from   db_api.common import constants as COMMON_CONSTANTS

from db_api.extensions    import db, migrate, socketio
from db_api.models        import UsersModel, TagsNotesTable, TagsModel, NotesModel
from db_api.database      import AppuntiDB
from db_api.api.UsersAPI  import UsersAPI, UserAPI
from db_api.api.NotesAPI  import NotesAPI, NoteAPI, NoteFilesAPI, NoteFilesPageAPI, NotesFilesPageFromAMQP_API
from db_api.api.SearchAPI import SearchAPI
from db_api.api.NotesWS   import NotesSocketIO   ### TODO: Better name
from db_api.amqp          import AMQP

def create_app(config=None, return_db=False):
    """Create a Flask app."""

    app_name = Config.DefaultConfig.PROJECT
    app = Flask(app_name, instance_path=COMMON_CONSTANTS.INSTANCE_FOLDER_PATH, instance_relative_config=True)
    configure_app(app, config)
    exts = configure_extensions(app, db)
    configure_resources(app)
    if return_db:
        return app, exts[1]
    else:
        return app, exts[3]

def configure_app(app, config=None):
    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(Config.DefaultConfig)

    if config:
        app.config.from_object(config)
        return

    # get mode from os environment
    application_mode = os.getenv('APPLICATION_MODE', 'LOCAL')
    app.config.from_object(Config.get_config(application_mode))


def configure_resources(flask_api):
    pass

def configure_extensions(app, db):
    # Flask-SQLAlchemy
    with app.app_context():
        db.init_app(app)
        #if app.SQLALCHEMY_DATABASE_URI == 'sqlite:////tmp/test.db':
        #    db.create_all()
        db.create_all()
    # Instatiate my database wrapper class
    DB = AppuntiDB(db, UsersModel, NotesModel, TagsModel,
                   {'account_id':app.config['B2_ACCOUNT_ID'],
                    'application_key': app.config['B2_APPLICATION_KEY'],
                    'bucket_id':app.config['B2_BUCKET_ID'],
                    'bucket_name': app.config['B2_BUCKET_NAME']}
                   )

    # Flask-RESTful init and add resource
    flask_api = Api(app)
    flask_api.add_resource(UsersAPI, COMMON_CONSTANTS.BASE_URI+'/users', resource_class_args=[DB])
    flask_api.add_resource(UserAPI,  COMMON_CONSTANTS.BASE_URI+'/users/<uid>', resource_class_args=[DB])
    flask_api.add_resource(NotesAPI, COMMON_CONSTANTS.BASE_URI+'/notes', resource_class_args=[DB])
    flask_api.add_resource(NoteAPI,  COMMON_CONSTANTS.BASE_URI+'/notes/<nid>', resource_class_args=[DB])
    flask_api.add_resource(SearchAPI, COMMON_CONSTANTS.BASE_URI+'/search', resource_class_args=[DB])
    flask_api.add_resource(NoteFilesAPI, COMMON_CONSTANTS.BASE_URI+'/files/<nid>', resource_class_args=[DB])
    flask_api.add_resource(NoteFilesPageAPI, COMMON_CONSTANTS.BASE_URI+'/files/<nid>/<page>', resource_class_args=[DB])
    flask_api.add_resource(NotesFilesPageFromAMQP_API, COMMON_CONSTANTS.BASE_URI+'/amqp/<nid>/<page>/<userID>', resource_class_args=[DB])



    # Flask-Sockets
    ### TODO Find a more Pythonic way, this kind of workaroud sucks in every language
    # websocket.init_app(app)
    # notes_ws = WS(DB)
    # @websocket.route('/ws')
    # def WSPageHandler(ws):
    #     return notes_ws.WSPageHandler(ws)
    notes_ws = NotesSocketIO(DB)
    socketio.init_app(app)
    socketio.on_event('connect',    notes_ws.on_connect,    namespace='/ws')
    socketio.on_event('disconnect', notes_ws.on_disconnect, namespace='/ws')
    socketio.on_event('json',       notes_ws.on_json,       namespace='/ws')

    return db, DB, flask_api, socketio
