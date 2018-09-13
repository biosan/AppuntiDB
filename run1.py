#!env/bin/python3

import os
from db_api import create_app

import tornado.httpserver
from tornado.ioloop import IOLoop

app, tornado_complete_app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    http_server = tornado.httpserver.HTTPServer(tornado_complete_app)
    http_server.listen(port)
    IOLoop.instance().start()
