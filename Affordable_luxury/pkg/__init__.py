
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from pkg import config


csrf = CSRFProtect()


def create_app():
    from pkg.models import db
    app=Flask(__name__,instance_relative_config=True)
    app.config.from_pyfile('config.py',silent=True)
    app.config.from_object(config.TestConfig)
    db.init_app(app) #we moved the instantiation of db to models.py
    csrf.init_app(app)  #initializing the app with CSRFProject object
    migrate = Migrate(app,db)

    return app


app = create_app() # call create_app to make app available here
from pkg import routes,admin_routes