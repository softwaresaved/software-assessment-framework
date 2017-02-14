from flask import Flask
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config['SECRET_KEY'] = 'change me'
Bootstrap(app)

from app import views


