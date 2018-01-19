from flask_wtf import FlaskForm

from wtforms import validators
from wtforms import BooleanField, IntegerField


class SubForm(FlaskForm):

    source_id = IntegerField(label="source id", validators=[
        validators.DataRequired()
    ])
    user_id = IntegerField(label="user id", validators=[
        validators.DataRequired()
    ])
