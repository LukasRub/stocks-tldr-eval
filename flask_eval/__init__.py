import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
   
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://wiruisxmoktlwj:3d4337c024090a3677e6fa43571b041c6d9cd978a3d1d4c43878871534fd9ebe@ec2-54-195-246-55.eu-west-1.compute.amazonaws.com:5432/d3hs5t3ohu0s0g"

    db = SQLAlchemy()
    db.init_app(app)


    from . import task_one
    app.register_blueprint(task_one.bp)

    from . import task_two
    app.register_blueprint(task_two.bp)

    @app.route("/")
    def index():
        return "Nice"

    return app