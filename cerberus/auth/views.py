from flask import (
    flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from cerberus.db import get_db,close_db

from . import auth


# -------------------------------------------------------------------------------------------
# REGISTER
@auth.route('/register', methods=('GET', 'POST'))
def register():
    # if request.method == 'POST':
    #     username = request.form['username']
    #     password = request.form['password']
    #     db = get_db()
    #     error = None
    #     if not username:
    #         error = 'Username is required.'
    #     elif not password:
    #         error = 'Password is required.'

    #     if error is None:
    #         try:
    #             db.execute(
    #                 "INSERT INTO user (username, password) VALUES (?, ?)",
    #                 (username, generate_password_hash(password)),
    #             )
    #             db.commit()   
    #         except db.IntegrityError:
    #             error = f"User {username} is already registered."
    #         else:
    #             # db.close()
    #             close_db()
    #             return redirect(url_for("auth.login"))

    #     flash(error)

    # return render_template('auth/register.html')
    flash("Registration is disabled.", "warning")
    return redirect(url_for("auth.login"))


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
        # close_db()
        

