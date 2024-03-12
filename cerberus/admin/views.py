import functools
from flask import (
    flash, g, redirect, render_template, request, session, url_for
)

from cerberus.db import get_db,close_db
from cerberus.auth import check_conn, login_required

from . import admin
from cerberus import projects
from cerberus.core.views import user_has_write_permission

def admin_required_local(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user['admin']:
            flash("You do not have permission to access this page.", "warning")
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# index admin (tabla users y projects)
@admin.route('/')
@login_required
@admin_required_local
def index():
    from cerberus.db import get_user_projects_info, get_users, get_user, get_projects, get_project
    data=[get_users(),get_projects()]
    return render_template('admin/index.html',
                        projects=projects,
                        title='Admin',
                        data=data,
                        writePermission=user_has_write_permission())

# Info usuario (usuario y proyectos asociados)
@admin.route('/user/<int:id>')
@login_required
@admin_required_local
def user(id):
    from cerberus.db import get_user_projects_info, get_users, get_user, get_projects, get_project
    data=[get_user(id),get_user_projects_info(id)]
    return render_template('admin/user.html',
                        projects=projects,
                        title='Admin',
                        data=data,
                        writePermission=user_has_write_permission())

# Edit user
@login_required
@admin_required_local
@admin.route('/user/<int:id>/edit', methods=['GET','POST'])
def edit_user(id):
    if request.method == 'POST':
        username = request.form.get('username')
        admin = 1 if request.form.get('admin') == 'on' else 0
        print(username,admin)
        db = get_db()
        # check if username exists
        error = None
        if not username:
            error = 'Username is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ? AND id != ?', (username, id)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is not None:
            flash(error, 'danger')
            return redirect(url_for('admin.edit_user', id=id))
        
        db = get_db()
        db.execute(
            'UPDATE user SET username = ?, admin = ? WHERE id = ?',
            (username, admin, id)
        )
        db.commit()
        flash('User updated', 'success')
    # else: 
    from cerberus.db import get_user_projects_info, get_users, get_user, get_projects, get_project
    data=[get_user(id),get_user_projects_info(id)]
    print(data[1])

    return render_template('admin/edit_user.html',
        projects=projects,
        title='Admin',
        data=data,
        writePermission=user_has_write_permission())

# Edit user
@login_required
@admin_required_local
@admin.route('/user/<int:id>/edit/add', methods=['POST'])
def edit_user_add(id):
    if request.method == 'POST':
        project = request.form.get('project')
        role = request.form.get('role')
        print(project,role)
        db = get_db()
        # get project id
        project = db.execute(
            'SELECT id FROM projects WHERE name = ?', (project,)
        ).fetchone()[0]
        # check if role association exists
        error = None
        if db.execute(
            'SELECT * FROM user_projects WHERE id_user = ? AND id_project = ?', (id, project)
        ).fetchone() is not None:
            error = 'User {} is already associated with project {}.'.format(id, project)

        if error is not None:
            flash(error, 'danger')
            return redirect(url_for('admin.edit_user', id=id))
        
        db = get_db()
        db.execute(
            'INSERT INTO user_projects (id_user, id_project, role) VALUES (?, ?, ?)',
            (id, project, role)
        )
        db.commit()
        flash('User updated', 'success')        

    return redirect(url_for('admin.edit_user', id=id))

# Edit user (remove project association)
@login_required
@admin_required_local
@admin.route('/user/<int:id>/edit/remove/<int:id_project>', methods=['GET'])
def edit_user_remove(id, id_project):
    db = get_db()
    db.execute('DELETE FROM user_projects WHERE id_user = ? AND id_project = ?', (id, id_project))
    db.commit()
    flash('User updated', 'success')
    return redirect(url_for('admin.edit_user', id=id))


@login_required
@admin_required_local
@admin.route('/user/<int:id>/delete', methods=['GET'])
def delete_user(id):
    print(id, g.user['id'])
    error = None
    if id == g.user['id']:
        error = 'You cannot delete yourself'        
    elif id==1:
        error='You cannot delete the admin'
    if error is not None:
        flash(error, 'danger')
        return redirect(url_for('admin.index'))
    else:    
        db = get_db()
        db.execute('DELETE FROM user_projects WHERE id_user = ?', (id,))
        db.execute('DELETE FROM user WHERE id = ?', (id,))
        db.commit()

        flash('User deleted', 'success')
        return redirect(url_for('admin.index'))
    
# Info proyecto (proyecto y usuarios asociados)
@admin.route('/project/<int:id>')
@login_required
@admin_required_local
def project(id):
    from cerberus.db import get_user_projects_info, get_users_by_project, get_user, get_projects, get_project
    data=[get_project(id),get_users_by_project(id)]
    print(data[1])

    return render_template('admin/project.html',
                        projects=projects,
                        title='Admin',
                        data=data,
                        writePermission=user_has_write_permission())

# Info proyecto (proyecto y usuarios asociados)
@admin.route('/project/<int:id>/edit')
@login_required
@admin_required_local
def edit_project(id):
    # else: 
    from cerberus.db import get_user_projects_info, get_users, get_user, get_projects, get_project,get_users_by_project
    data=[get_project(id),get_users_by_project(id), get_users()]

    return render_template('admin/edit_project.html',
        projects=projects,
        title='Admin',
        data=data,
        writePermission=user_has_write_permission())

@login_required
@admin_required_local
@admin.route('/project/<int:id>/edit/add', methods=['POST'])
def edit_project_add(id):
    if request.method == 'POST':
        user = request.form.get('user')
        role = request.form.get('role')
        print(user,role)
        db = get_db()

        # check if role association exists
        error = None
        if db.execute(
            'SELECT * FROM user_projects WHERE id_user = ? AND id_project = ?', (user, id)
        ).fetchone() is not None:
            error = 'User {} is already associated with project {}.'.format(user, id)

        if error is not None:
            flash(error, 'danger')
            return redirect(url_for('admin.edit_project', id=id))
        
        db = get_db()
        db.execute(
            'INSERT INTO user_projects (id_user, id_project, role) VALUES (?, ?, ?)',
            (user, id, role)
        )
        db.commit()
        flash('Project updated', 'success')        

    return redirect(url_for('admin.edit_project', id=id))

# Edit project (remove user association)
@login_required
@admin_required_local
@admin.route('/project/<int:id>/edit/remove/<int:id_user>', methods=['GET'])
def edit_project_remove(id, id_user):
    db = get_db()
    db.execute('DELETE FROM user_projects WHERE id_user = ? AND id_project = ?', (id_user, id))
    db.commit()
    flash('Project updated', 'success')
    return redirect(url_for('admin.edit_project', id=id))

@login_required
@admin_required_local
@admin.route('/user/new', methods=['POST'])
def new_user():
    from cerberus.db import get_user_projects_info, get_users, get_user, get_projects, get_project
    from cerberus.utils import generate_random_password
    from werkzeug.security import generate_password_hash
    if request.method == 'POST':
        username = request.form.get('username')

        db =get_db()
        db = get_db()
        error = None
        if not username:
            error = 'Username is required.'
        if error is None:
            try:
                password=generate_random_password()
                print(password)
                u=db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
                flash(f"Credentials: {username} - {password}","success")
                return redirect(url_for('admin.edit_user',id=u.lastrowid))
            except db.IntegrityError:
                error = f"User {username} is already registered."
                flash(error,"danger")
                return redirect(url_for('admin.new_user'))
        else:
            flash(error,"danger")

    return redirect(request.referrer)