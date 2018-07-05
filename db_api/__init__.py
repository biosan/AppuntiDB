import os

from flask import Flask
from flask_restful import Api

import db_api.config as     Config
from   db_api.common import constants as COMMON_CONSTANTS

from db_api.extensions    import db, migrate, auth
from db_api.models        import UsersModel, TagsNotesTable, TagsModel, NotesModel, CategoryTagsTable, CategoryModel
from db_api.database      import AppuntiDB
from db_api.api.UsersAPI  import UsersAPI, UserAPI
from db_api.api.NotesAPI  import NotesAPI, NoteAPI, NoteFilesAPI, NoteFilesPageAPI, NotesFilesPageFromAMQP_API
from db_api.api.SearchAPI import SearchAPI
from db_api.api.NotesWS   import get_tornado_app
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
        db.create_all()
    # Instatiate my database wrapper class
    DB = AppuntiDB(db, UsersModel, NotesModel, TagsModel, CategoryModel,
                   {'account_id':app.config['B2_ACCOUNT_ID'],
                    'application_key': app.config['B2_APPLICATION_KEY'],
                    'bucket_id':app.config['B2_BUCKET_ID'],
                    'bucket_name': app.config['B2_BUCKET_NAME']}
                   )

    # Flask-RESTful init and add resource
    flask_api = Api(app, prefix=COMMON_CONSTANTS.BASE_URI)
    flask_api.add_resource(UsersAPI, '/users', resource_class_args=[DB])
    flask_api.add_resource(UserAPI,  '/users/<uid>', resource_class_args=[DB])
    flask_api.add_resource(NotesAPI, '/notes', resource_class_args=[DB])
    flask_api.add_resource(NoteAPI,  '/notes/<nid>', resource_class_args=[DB])
    flask_api.add_resource(SearchAPI, '/search', resource_class_args=[DB])
    flask_api.add_resource(NoteFilesAPI, '/files/<nid>', resource_class_args=[DB])
    flask_api.add_resource(NoteFilesPageAPI, '/files/<nid>/<page>', resource_class_args=[DB])
    flask_api.add_resource(NotesFilesPageFromAMQP_API, '/amqp/<nid>/<page>/<userID>', resource_class_args=[DB])

    ### Configure Tornado
    tornado_complete_app = get_tornado_app(app, DB)

    ### Configure authentication
    auth.verify_password(DB.authenticate_user)

    return db, DB, flask_api, tornado_complete_app