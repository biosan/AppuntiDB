import os
from db_api.common.constants import INSTANCE_FOLDER_PATH

class BaseConfig(object):

   PROJECT = "db-api"

   # Get app root path, also can use flask.root_path.
   PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

   DEBUG = False
   TESTING = False

   B2_ACCOUNT_ID      = os.environ.get('B2_ACCOUNT_ID')#, '768fd2cae9aa')
   B2_APPLICATION_KEY = os.environ.get('B2_APPLICATION_KEY')#, '000e640240ab835b063f8c8cc27d45ef97f43d1f31')

   SQLALCHEMY_DATABASE_URI = ''

   AMQP_BROKER_URL = os.environ.get('AMQP_BROKER_URL', 'localhost')

   PORT = 80

class DefaultConfig(BaseConfig):

   # Statement for enabling the development environment
   DEBUG = True

   # Secret key for signing cookies
   SECRET_KEY = 'development key'



class LocalConfig(DefaultConfig):
    # config for local development
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/db.sqlite'
    AMQP_BROKER_URL         = 'localhost'
    B2_BUCKET_ID            = 'f796a86f6de22cfa6e190a1a'
    B2_BUCKET_NAME          = 'appunti-testing-bucket'
    PORT = 5000



class StagingConfig(DefaultConfig):
    # config for staging environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:////tmp/db.sqlite')



class ProdConfig(DefaultConfig):
    # config for production environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    AMQP_BROKER_URL         = os.environ.get('AMQP_BROKER_URL')
    B2_BUCKET_ID            = 'c7e6f83f4d122cfa6e190a1a'
    B2_BUCKET_NAME          = 'appunti-main-bucket'



def get_config(MODE):
    SWITCH = {
      'LOCAL'     : LocalConfig,
      'STAGING'   : StagingConfig,
      'PRODUCTION': ProdConfig
    }
    return SWITCH[MODE]
