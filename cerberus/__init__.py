import os

from flask import Flask

projects = []
def create_app():
    global projects
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='default',
    )
    # if config file exists, load it
    app.config.from_pyfile('config.py', silent=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, app.config['DATABASE']),
        PROJECTS_PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)),app.config['PROJECTS_PATH'])
    )


    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Get all existing projects
    # projects_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),app.config['PROJECTS_PATH'])
    # ensure the projects folder exists
    try:
        # os.makedirs(projects_path)
        os.makedirs(app.config['PROJECTS_PATH'])
    except OSError:
        pass

    

    # file_names = os.listdir(projects_path)
    file_names = os.listdir(app.config['PROJECTS_PATH'])
    # Eliminar el texto ".db" del final de cada nombre de archivo
    projects = [name.replace('.db', '') for name in file_names]

    # Commands cli database
    from . import db
    db.init_app(app)


    # BLUEPRINTS
    from .auth import auth
    # /auth
    app.register_blueprint(auth)


    from .core import core
    # /
    app.register_blueprint(core)

    from .admin import admin
    # /admin
    app.register_blueprint(admin)

    return app