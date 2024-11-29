from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_babel import Babel
from flask_login import LoginManager

def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

app = Flask(__name__)
app.config.from_object('config')

babel = Babel(app, locale_selector=get_locale)
admin = Admin(app, template_mode='bootstrap4')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

from app.models import User  
from app import views, models 

@login_manager.user_loader
def load_user(id):
    if id is None:
        return None
    try:
        user = User.query.get(int(id))
        return user
    except ValueError:
        return None