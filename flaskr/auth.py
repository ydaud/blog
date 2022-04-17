import functools

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from flask.views import MethodView

BP_NAME = "auth"
auth_bp = Blueprint(BP_NAME, __name__, url_prefix='/auth')


class Register(MethodView):
	
	def get(self):
		return render_template('auth/register.html')

	def post(self):
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
				return redirect(url_for("auth.login"))

		flash(error)
		return render_template('auth/register.html')


class Login(MethodView):

	def get(self):
		return render_template('auth/login.html')

	def post(self):
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
			return redirect(url_for('blog.index'))

		flash(error)
		return render_template('auth/login.html')


class Logout(MethodView):

	def get(self):
		session.clear()
		return redirect(url_for('blog.index'))


@auth_bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')

	if user_id is None:
		g.user = None
	else:
		g.user = get_db().execute(
			'SELECT * FROM user WHERE id = ?', (user_id,)
		).fetchone()

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(*args, **kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))

		return view(*args, **kwargs)

	return wrapped_view


register_view = Register.as_view("register")
login_view = Login.as_view("login")
logout_view = Logout.as_view("logout")

auth_bp.add_url_rule(
    "/register",
    view_func=register_view,
    methods=["GET", "POST"],
)

auth_bp.add_url_rule(
    "/login",
    view_func=login_view,
    methods=["GET", "POST"],
)

auth_bp.add_url_rule(
    "/logout",
    view_func=logout_view,
    methods=["GET"],
)






# @bp.route('/register', methods=('GET', 'POST'))
# def register():
# 	if request.method == 'POST':
# 		username = request.form['username']
# 		password = request.form['password']
# 		db = get_db()
# 		error = None

# 		if not username:
# 			error = 'Username is required.'
# 		elif not password:
# 			error = 'Password is required.'

# 		if error is None:
# 			try:
# 				db.execute(
# 					"INSERT INTO user (username, password) VALUES (?, ?)",
# 					(username, generate_password_hash(password)),
# 				)
# 				db.commit()
# 			except db.IntegrityError:
# 				error = f"User {username} is already registered."
# 			else:
# 				return redirect(url_for("auth.login"))

# 		flash(error)

# 	return render_template('auth/register.html')

# @bp.route('/login', methods=('GET', 'POST'))
# def login():
# 	if request.method == 'POST':
# 		username = request.form['username']
# 		password = request.form['password']
# 		db = get_db()
# 		error = None
# 		user = db.execute(
# 			'SELECT * FROM user WHERE username = ?', (username,)
# 		).fetchone()

# 		if user is None:
# 			error = 'Incorrect username.'
# 		elif not check_password_hash(user['password'], password):
# 			error = 'Incorrect password.'

# 		if error is None:
# 			session.clear()
# 			session['user_id'] = user['id']
# 			return redirect(url_for('index'))

# 		flash(error)

# 	return render_template('auth/login.html')

# @bp.route('/logout')
# def logout():
# 	session.clear()
# 	return redirect(url_for('index'))