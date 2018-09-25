from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from src.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)

login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

from src.posts.routes import posts
from src.users.routes import users
from src.main.routes import main
from src.contact.routes import contact
from src.search.routes import search
from src.errors.error_handlers import errors

app.register_blueprint(posts)
app.register_blueprint(users)
app.register_blueprint(main)
app.register_blueprint(contact)
app.register_blueprint(search)
app.register_blueprint(errors)
