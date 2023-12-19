import functools

from flask import (
    Blueprint, g, redirect, url_for, request, render_template
)
core = Blueprint('core', __name__, url_prefix='/')

from . import views
