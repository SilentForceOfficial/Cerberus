import functools

from flask import (
    Blueprint, flash, g, redirect, url_for
)
admin = Blueprint('admin', __name__, url_prefix='/admin')

from . import views


# Requerir auth en otras vistas
def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user['admin']:
            flash('Unauthorized', 'danger')
            return redirect(url_for('core.dashboard'))

        return view(**kwargs)

    return wrapped_view
