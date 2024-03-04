import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

        
def init_db(user, password):
    from werkzeug.security import check_password_hash, generate_password_hash
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    # close_db()
    # Crear usuario por defecto
    try:
        db.execute(
            "INSERT INTO user (username, password, admin) VALUES (?, ?, ?)",
            (user, generate_password_hash(password), 1),
        )
        db.commit()
    except db.IntegrityError:
        error = f"User is already registered."
    try:
        from cerberus import projects
        for i in projects:
            db.execute(
                "INSERT INTO projects (name) VALUES (?)",
                (i,),
            )
        db.commit()

    except db.IntegrityError:
        error = f"Project {i} is already registered."
    else:
        # db.close()
        close_db()


@click.command('setup')
@click.option('--user', default='cerberus', help='Username')
@click.option('--password', default='cerberus', help='Password of the user')
def init_db_command(user, password):
    """Clear the existing data and create new tables."""
    init_db(user, password)
    click.echo('Database successfully created.')
    

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


# Other functions
def get_projects():
    db = get_db()
    projects = db.execute(
        # "SELECT id, name FROM projects"
        '''
        SELECT projects.id, projects.name, COALESCE(user_count, 0) AS user_count
        FROM projects
        LEFT JOIN (
            SELECT id_project, COUNT(id_user) AS user_count
            FROM user_projects
            GROUP BY id_project
        ) AS project_user_count ON projects.id = project_user_count.id_project;

    '''
    ).fetchall()
    return projects

def get_project(id):
    db = get_db()
    project = db.execute(
        "SELECT id, name FROM projects WHERE id = ?", (id,)
    ).fetchone()
    return project

def get_users():
    db = get_db()
    users = db.execute(
        '''SELECT user.id, user.username, user.admin, COALESCE(COUNT(user_projects.id_user), 0) AS project_count 
            FROM user 
            LEFT JOIN user_projects ON user_projects.id_user = user.id 
            GROUP BY user.id, user.username, user.admin
        '''
    ).fetchall()
    return users
def get_users_by_project(id):
    db = get_db()
    users = db.execute(
        '''SELECT user.id, user.username, user.admin, user_projects.role
        FROM user_projects
        JOIN user ON user_projects.id_user = user.id
        WHERE user_projects.id_project = ?
        ''', (id,)
    ).fetchall()
    return users

def get_user(id):
    db = get_db()
    user = db.execute(
        '''SELECT user.id, user.username, user.admin, COALESCE(COUNT(user_projects.id_user), 0) AS project_count 
            FROM user 
            LEFT JOIN user_projects ON user_projects.id_user = user.id
            WHERE user.id = ?
            GROUP BY user.id, user.username, user.admin
        ''', (id,)
    ).fetchone()
    return user

# Obtener los proyectos de un usuario, con el nombre del proyecto y el rol del usuario en ese proeycto
def get_user_projects_info(user_id):
    db = get_db()
    projects = db.execute(
        # "SELECT project.id, projects.name, user_projects.role, FROM user_projects JOIN projects ON user_projects.id_project = projects.id WHERE user_projects.id_user = ?", (user_id,)
        '''SELECT projects.id, projects.name, user_projects.role
            FROM user_projects
            JOIN projects ON user_projects.id_project = projects.id
            WHERE user_projects.id_user = ?''', (user_id,)
    ).fetchall()
    return projects