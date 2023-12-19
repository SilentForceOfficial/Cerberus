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
            "INSERT INTO user (username, password) VALUES (?, ?)",
            (user, generate_password_hash(password)),
        )
        db.commit()   
    except db.IntegrityError:
        error = f"User is already registered."
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