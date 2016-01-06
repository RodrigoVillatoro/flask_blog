import logging
import os

from config_secret import *

LOG_LEVEL = logging.WARNING


class Configuration:
    APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
    DEBUG = True
    SECRET_KEY = YOUR_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = YOUR_DATABASE % APPLICATION_DIR
    STATIC_DIR = os.path.join(APPLICATION_DIR, 'static')
    IMAGES_DIR = os.path.join(STATIC_DIR, 'images')

