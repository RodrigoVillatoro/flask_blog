from flask import Flask, g
from flask_login import LoginManager, current_user

from flask_bcrypt import Bcrypt
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_restless import APIManager
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler

from config import Configuration, LOG_LEVEL


app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = APIManager(app, flask_sqlalchemy_db=db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.before_request
def _before_request():
    g.user = current_user

bcrypt = Bcrypt()

file_handler = RotatingFileHandler('blog.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(LOG_LEVEL)