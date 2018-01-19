import os
from db_api.common.constants import INSTANCE_FOLDER_PATH

class BaseConfig(object):

   PROJECT = "db-api"

   # Get app root path, also can use flask.root_path.
   PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

   DEBUG = False
   TESTING = False

   ADMINS = ['alessandro@biondi.me']

   # http://flask.pocoo.org/docs/quickstart/#sessions
   SECRET_KEY = 'secret key'

   AWS_KEY = ''

   B2_KEY = ''

   SQLALCHEMY_DATABASE_URI = ''

   AMQP_SERVER = ''



class DefaultConfig(BaseConfig):

   # Statement for enabling the development environment
   DEBUG = True

   # Secret key for signing cookies
   SECRET_KEY = 'development key'



class LocalConfig(DefaultConfig):
    # config for local development
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/db.sqlite'
    pass



class StagingConfig(DefaultConfig):
    # config for staging environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:////tmp/db.sqlite')
    pass



class ProdConfig(DefaultConfig):
    # config for production environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:////tmp/db.sqlite')
    pass



def get_config(MODE):
    SWITCH = {
      'LOCAL'     : LocalConfig,
      'STAGING'   : StagingConfig,
      'PRODUCTION': ProdConfig
    }
    return SWITCH[MODE]
