from flask import Flask
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Set up logging
handler = RotatingFileHandler('saf.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s %(funcName)s() - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)


app.config['SECRET_KEY'] = 'change me'
Bootstrap(app)

from app import views


