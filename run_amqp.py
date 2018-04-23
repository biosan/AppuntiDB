#!env/bin/python3

import os
from db_api.amqp import AMQP

if __name__ == '__main__':
    amqp = AMQP(os.environ.get('AMQP_BROKER_URL'), 'users_queue', 'notes_queue', 'SEARCH_QUERY_REQUEST', 'SEARCH_QUERY_RESPONSE')
    amqp.start()
