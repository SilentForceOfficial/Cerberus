import functools

from flask import (
    Blueprint, flash, g, redirect, url_for
)
auth = Blueprint('auth', __name__, url_prefix='/auth')

from . import views


# Requerir auth en otras vistas
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# Chack neo4j en otras vistas
def check_conn(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):

        if g.user[3] is None or g.user[4] is None or g.user[5] is None:
            flash("Neo4j connection not set. Please, go to settings and set it.", "warning")
            return redirect(url_for('core.dashboard'))
        else:
            from neo4j import GraphDatabase
            # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
            URI = g.user[3]
            AUTH = (g.user[4], g.user[5])

            try:
                with GraphDatabase.driver(URI, auth=AUTH) as driver: 
                    driver.verify_connectivity()
            except:
                flash("Error connecting to database. Is the database up?", "warning")
                return redirect(url_for('core.dashboard'))

        return view(**kwargs)

    return wrapped_view