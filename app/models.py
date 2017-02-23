import logging
from . import app
from flask_sqlalchemy import SQLAlchemy
import datetime
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
    submitted = db.Column(db.DateTime, default=datetime.datetime.now())
    url = db.Column(db.Text)
    scores = db.relationship('Score', backref='software', lazy='dynamic')


class Score(db.Model):
    """
    Entity class for the result of running a metric against an item of software
    """
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    software_id = db.Column(db.Integer, db.ForeignKey('software.id'))
    category = db.Column(db.Text)
    short_description = db.Column(db.Text)
    long_description = db.Column(db.Text)
    value = db.Column(db.Integer)
    feedback = db.Column(db.Text)

    def __init__(self, software_id, category, short_description, long_description, value, feedback):
        self.software_id = software_id
        self.category = category
        self.short_description = short_description
        self.long_description = long_description
        self.value = value
        self.feedback = feedback


# Create database if required
if not os.path.exists(app.config['SQLALCHEMY_DATABASE_URI']):
    app.logger.info("Creating tables in data.sqlite")
    db.create_all()