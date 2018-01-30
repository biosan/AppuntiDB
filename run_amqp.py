#!env/bin/python3

import os
import db_api

app, DB= db_api.create_app(return_db=True)

if __name__ == '__main__':
    app.app_context().push()
    amqp = db_api.amqp.AMQP(app.config['AMQP_BROKER_URL'], DB, 'users_queue', 'notes_queue', 'search_queue')
    amqp.start()
