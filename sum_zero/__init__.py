import os

from flask import Flask, g, render_template, session
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Set configuration target file depending on environment
if os.environ.get('PRODUCTION'):
    app.config.from_object('heroku_config')
else:
    app.config.from_object('config')

db = SQLAlchemy(app)
mail = Mail(app)

# Configuring app for Flask-Login
from sum_zero.user.models import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user.login"
login_manager.session_protection = "strong" # Will log users out if IP or agent header changes

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

# Configuring app for SQL migration manager
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from sum_zero.user.views import mod as user_blueprint
app.register_blueprint(user_blueprint)

from sum_zero.summary.views import mod as summary_blueprint
app.register_blueprint(summary_blueprint)

from sum_zero.api.views import mod as api_blueprint
app.register_blueprint(api_blueprint)

from sum_zero.base_views.views import mod as base_blueprint
app.register_blueprint(base_blueprint)

app.debug = app.config['DEBUG']
