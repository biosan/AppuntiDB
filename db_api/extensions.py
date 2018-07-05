# Flask-SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime
from sqlalchemy.sql.functions import now
db = SQLAlchemy()
class Base(db.Model):
    __abstract__ = True
    created_on = Column(DateTime, default=now())
    updated_on = Column(DateTime, default=now(), onupdate=now())


# Flask Migration
from flask_migrate import Migrate
migrate = Migrate()


# Logging
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)


# Authentication
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()