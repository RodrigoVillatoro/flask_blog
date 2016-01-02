import os

from config_secret import *

class Configuration:
    APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
    DEBUG = True
    SECRET_KEY = YOUR_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = YOUR_DATABASE % APPLICATION_DIR
