import os

# Instance folder path, make it independent.
INSTANCE_FOLDER_PATH = os.path.join('/tmp', 'instance')

VERSION = '0.1'
BASE_URI = '/db/api/v{}'.format(VERSION)
