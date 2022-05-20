from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import path

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    # Config App
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'twitterosingtool2022scraper'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database///{DB_NAME}'

    db.init_app(app)
    migrate = Migrate(app, db)

    from .views import views # Routes of webapp

    app.register_blueprint(views, url_prefix='/') # Blueprint for views

    # Create database with models
    from .models import Target

    create_database(app)

    return app

def create_database(app):
    if not path.exists('tt_osint/database/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')