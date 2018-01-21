from flask import (abort, Blueprint, flash, g, redirect, request, render_template,
                    session, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from functools import wraps

from sum_zero import db
from sum_zero.user.forms import EditProfileForm, LoginForm, RegistrationForm
from sum_zero.user.models import User, UserAuth


mod = Blueprint('user', __name__, url_prefix="/user")

# Decorators
def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated():
            return f(*args, **kwargs)
        flash("Login required.")
        return redirect(url_for('user.login'))
    return wrapped

def is_user(f):
    def wrapped(*args, **kwargs):
        if current_user.id == kwargs.get('user_id'):
            return f(*args, **kwargs)
        raise Exception("Forbidden")
    return wrapped

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

@mod.route('/<user_id>/', methods=['GET', 'POST'])
def profile(user_id=None):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        abort(404)
    if user.id != current_user.id:
        profile = user.user_context()
        return render_template('user/profile.html', is_user=False, form=None, profile=profile)
    form = EditProfileForm()
    if form.validate_on_submit():
        # TODO: consider abstracting and moving this to background thread
        # TODO: separate out email changing to separate process
        user.first_name = form.first_name.data or user.first_name
        user.last_name = form.last_name.data or user.last_name
        user.bio = form.bio.data or user.bio
        db.session.add(user)
        db.session.commit()
        flash("Your profile has been updated.")
    # Populate profile form with existing user fields and render template
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.bio.data = user.bio
    profile = user.user_context()
    return render_template('user/profile.html', is_user=True, form=form, profile=profile)
