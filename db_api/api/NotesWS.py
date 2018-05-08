"""
WebSockets with Tornado
"""

import sys
import secrets
import json

import tornado.web
import tornado.websocket
import tornado.template
import tornado.gen
import tornado.wsgi



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello, world')

class WSHandler(tornado.websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super(WSHandler, self).__init__(application, request, **kwargs)

    def initialize(self, database):
        self.DB = database
        self.user_ID = None
        self.SID = None

    def open(self):
        self.SID = secrets.token_urlsafe(8)
        self.DB.ws_clients[self.SID] = self
        self.write_message("The server says: 'Hello'. Connection was accepted.")
        print('connection for client with SID: {0} opened...'.format(self.SID), file=sys.stderr)

    def on_message(self, message):
        print("Recived:", message)
        try:
            msg_json = json.loads(message)
            self.user_ID = msg_json['user_ID']
            self.DB.userID_to_SID[self.user_ID] = self.SID
        except:
            self.write_message("Error")
            print("Error reading json from websocket message", file=sys.stderr)
            return
        self.write_message("Welcome {} you are now connected".format(self.user_ID))
        print('New user_ID: {}'.format(self.user_ID), message, file=sys.stderr)

    def on_close(self):
        self.DB.ws_clients.pop(self.user_ID, None)
        self.DB.userID_to_SID.pop(self.user_ID)
        print('connection closed...', file=sys.stderr)


def get_tornado_app(app, database):
    """
    Get Tornado app
    """
    flask_app=tornado.wsgi.WSGIContainer(app)
    application = tornado.web.Application([
        (r'/tornado?', MainHandler),
        (r'/ws', WSHandler, {'database':database}),
        (r'.*',tornado.web.FallbackHandler,{'fallback':flask_app })
    ])
    return application
