import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verificar = request.form['verificar']
        email = request.form['email']
        db = get_db()
        error = None

        if not username:
            error = 'Se necesita Nombre de usuario.'
        elif not password:
            error = 'Se necesita contraseña requerida.'
        elif verificar != password:
            error = 'Las claves no coinciden.'
        elif not email:
            error = 'Se necesita email requerido.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, verificar, email) VALUES (?, ?, ?, ?)",
                    (username, generate_password_hash(password),verificar, email),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
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
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))


        flash(error)

    return render_template('auth/login.html')
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/modificar', methods=('GET', 'POST'))
def modificar():

    if request.method == 'POST':
        email = request.form['nuevoEmail']
        error = None
        db = get_db()
        if not email:
            error = 'modificar Email'

        if error is not None:
            db.execute(
                'UPDATE user SET email = ?'
                ' WHERE id = ?',
                (email, g.user[id],)
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('auth/modifyEmail.html')

@bp.route('/borUser', methods=('GET', 'POST'))
def borUser():
    if request.method == 'POST':
        error = None
        db = get_db()

        if error is not None:
            db.execute(
                'DELETE FROM user WHERE id = ?',
                ( g.user[id],)
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('auth/modifyEmail.html')
