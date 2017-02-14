import logging
from . import app
from flask_sqlalchemy import SQLAlchemy
import os


# SQLAlchemy setup
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, '../data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

class Software(db.Model):
    """
    Entity class for an item of software submitted for assessment
    """
    __tablename__ = 'software'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    version = db.Column(db.Text)
    submitter = db.Column(db.Text)
    submitted = db.Column(db.DateTime)
    url = db.Column(db.Text)

    def __init__(self, id, name, description, version, submitter, submitted, url):
        logging.debug("Creating new instance of Software: "+name)
        self.id = id
        self.name = name
        self.description = description
        self.version = version
        self.submitter = submitter
        self.submitted = submitted
        self.url = url

if not os.path.exists(app.config['SQLALCHEMY_DATABASE_URI'] ):
    logging.info("Creating tables in data.sqlite")
    db.create_all()