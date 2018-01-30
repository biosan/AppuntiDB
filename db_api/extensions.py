# Flask-SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Flask Migration
from flask_migrate import Migrate
migrate = Migrate()

# Flask-Sockets (WebSockets with gevent)
from flask_sockets import Sockets
websocket = Sockets()
