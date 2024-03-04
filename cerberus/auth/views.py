from flask import (
    flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from cerberus.db import get_db,close_db

from . import auth

import functools

# Requerir auth en otras vistas
def login_required_local(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

def admin_required_local(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user['admin']:
            flash("You do not have permission to access this page.", "warning")
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
# -------------------------------------------------------------------------------------------
# REGISTER
@auth.route('/register', methods=('GET', 'POST'))
@login_required_local
@admin_required_local
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()   
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # db.close()
                close_db()
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')
    # flash("Registration is disabled.", "warning")
    # return redirect(url_for("auth.login"))

# CHANGE PASSWORD
@auth.route('/reset_password', methods=('GET', 'POST'))
@login_required_local
def resetpass():

    if request.method == 'POST':
        password_actual = request.form['pass0']
        password_new = request.form['pass1']
        password_new2 = request.form['pass2']
        db = get_db()
        error = None
        if not password_actual or not password_new or not password_new2:
            error = 'Fill in all fields'
        elif not check_password_hash(g.user['password'], password_actual):
            error = 'Incorrect password'
        elif password_new != password_new2:
            error = 'Passwords do not match'
        elif password_actual == password_new:
            error = 'New password must be different from current password'

        if error is None:
            try:
                db.execute(
                    "UPDATE user SET password = ? WHERE username = ?",
                    (generate_password_hash(password_new), g.user['username'])),
                
                db.commit()   
            except db.IntegrityError:
                # error = f"User {username} is already registered."
                pass
            else:
                close_db()
                flash("Password changed successfully", "success")
                return redirect(url_for("core.dashboard"))

        flash(error,"danger")

        return render_template('auth/resetpass.html')
    elif request.method == 'GET':
        return render_template('auth/resetpass.html')


# LOGIN
@auth.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            # error = 'Incorrect username.'
            error = 'Bad username or password.'
        elif not check_password_hash(user['password'], password):
            # error = 'Incorrect password.'
            error = 'Bad username or password.'
        close_db()
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('core.dashboard'))

        flash(error)

    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db=get_db()
        g.user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        
        if g.user["admin"]:
            from cerberus import projects
            g.projects = projects
        else:
            # Proyectos del usuario
            _ = db.execute(
                '''SELECT projects.name 
                    FROM projects 
                    INNER JOIN user_projects ON projects.id = user_projects.id_project
                    INNER JOIN user ON user.id = user_projects.id_user
                    WHERE user.username = ?''', (g.user["username"],)
            ).fetchall()
            g.projects = [i[0] for i in _]
        

