#!env/bin/python3

import os
from db_api import create_app

app, socketio = create_app()

if __name__ == '__main__':
    #from gevent import pywsgi
    #from geventwebsocket.handler import WebSocketHandler
    #app.debug = True
    #server = pywsgi.WSGIServer((app.config['BASE_ADDRESS'],
    #                            app.config['PORT']),
    #                            app,
    #                            handler_class=WebSocketHandler)
    #server.serve_forever()
    #port = int(os.environ.get("PORT", 5000))
    #app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
    socketio.run(app, port=app.config['PORT'], host=app.config['BASE_ADDRESS'])
