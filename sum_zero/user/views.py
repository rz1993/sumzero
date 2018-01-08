from flask import (abort, Blueprint, flash, g, redirect, request, render_template,
                    session, url_for)
from flask_login import login_required, login_user, logout_user

from sum_zero.user.forms import RegistrationForm, LoginForm
from sum_zero.user.models import User, UserAuth


mod = Blueprint('user', __name__, url_prefix="/user")

# Decorators
def login_required(f):
    def wrapped_f(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        flash("Login required.")
        return redirect(url_for('user.login'))
    return wrapped_f

# Views
@mod.route('/register', methods=['GET', 'POST'])
def register():
    # TODO: initiate task of sending confirmation email
    form = RegistrationForm()
    if form.validate_on_submit():
        user_auth = form.get_user_auth_data()
        user_profile = form.get_user_profile_data()

        # User backend validation and creation
        if UserAuth.validate_new_user(user_auth):
            user = UserAuth.create_user(user_auth, user_profile)
            login_user(user)

            return redirect(url_for('user.registration_success'))
        flash("Email is already in use.")
    return render_template('user/register.html', form=form)

@mod.route('/registration_success')
def registration_success():
    return render_template('user/success.html')

@mod.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print("Form validated. Authenticating...")
        user = UserAuth.authenticate(form.email.data, form.password.data)
        if user:
            login_user(user, remember=form.remember_me.data)
            flash("Welcome back!")
            return redirect(url_for('index'))
        flash("Invalid username or password.")
    return render_template('user/login.html', form=form)

@mod.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('index'))

@mod.route('/<user_id>/')
def profile(user_id=None):
    if user_id is None:
        abort(404)
    user = User.query.filter(id=user_id).first()
    if not user:
        abort(404)
    return render_template('user/profile.html', user=user)
