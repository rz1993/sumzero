from flask_wtf import FlaskForm
from wtforms import validators
from wtforms import BooleanField, PasswordField, StringField, SubmitField


class RegistrationForm(FlaskForm):
    first_name = StringField("First Name: ", validators=[
        validators.DataRequired("first name is required.")])
    last_name = StringField("Last Name: ", validators=[
        validators.DataRequired("last name is required.")])
    email = StringField("Email: ", validators=[
        validators.DataRequired("email is required"),
        validators.Email("invalid email format")])
    password = PasswordField("Password: ", validators=[
        validators.DataRequired("password is required"),
        validators.Length(min=6, message="password needs to be at least 6 characters")])
    submit = SubmitField('Register')

    def get_user_auth_data(self):
        return {'username': self.email.data, 'password': self.password.data}

    def get_user_profile_data(self):
        return {'email': self.email.data, 'first_name': self.first_name.data,
            'last_name': self.last_name.data}


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[
        validators.DataRequired("email is required"),
        validators.Email("invalid email")])
    password = PasswordField("Password: ", validators=[
        validators.DataRequired("password is required"),
        validators.Length(min=6, message="password needs to be at least 6 characters")])
    remember_me = BooleanField("Remember me:")
    submit = SubmitField('Login')
