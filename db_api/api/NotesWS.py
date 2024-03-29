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

    ###
    ### Disable cross-origin checks
    ###
    ### Warning
    ### This is an important security measure; don’t disable it without understanding the security implications.
    ### In particular, if your authentication is cookie-based, you must either restrict the origins allowed by check_origin()
    ### or implement your own XSRF-like protection for websocket connections. See these articles for more.
    ### Read more: http://www.tornadoweb.org/en/stable/websocket.html#tornado.websocket.WebSocketHandler.check_origin
    ###
    ### TODO: Please enable origin check when running in production!!!
    ###
    def check_origin(self, origin):
        return True

    def open(self):
        self.SID = secrets.token_urlsafe(8)  ### TODO: Substitute with IDTools.generate_id ???
        self.DB.ws_clients[self.SID] = self
        self.write_message("The server says: 'Hello'. Connection was accepted.")
        ###LOGGING###print('connection for client with SID: {0} opened...'.format(self.SID), file=sys.stderr)

    def on_message(self, message):
        ###LOGGING###print("Recived:", message)
        try:
            msg_json = json.loads(message)
            self.user_ID = msg_json['user_ID']
            self.DB.userID_to_SID[self.user_ID] = self.SID
        except:
            self.write_message("Error")
            ###LOGGING###print("Error reading json from websocket message", file=sys.stderr)
            return
        self.write_message("Welcome {} you are now connected".format(self.user_ID))
        ###LOGGING###print('New user_ID: {}'.format(self.user_ID), message, file=sys.stderr)

    def on_close(self):
        self.DB.ws_clients.pop(self.user_ID, None)
        self.DB.userID_to_SID.pop(self.user_ID)
        ###LOGGING###print('connection closed...', file=sys.stderr)


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