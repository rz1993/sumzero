from flask import url_for
from hashlib import md5
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sum_zero import app, db
from werkzeug.security import check_password_hash, generate_password_hash


class User(db.Model):
    """
    Basic user profile model built to be compatible with Flask-Login and
    has basic confirmation functionality and subscription functionality.
    """

    id = db.Column(db.Integer, primary_key=True)

    # User email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    is_enabled = db.Column(db.Boolean(), nullable=False, default=False)
    first_name = db.Column(db.String(50), nullable=False, default='')
    last_name = db.Column(db.String(50), nullable=False, default='')
    bio = db.Column(db.Text(), nullable=True)
    ig_handle = db.Column(db.String(50), nullable=True) # For avatar retrieval
    avatar_hash = db.Column(db.String(255), nullable=True)

    """ Following four methods required for Flask-Login session management."""
    def is_authenticated(self):
        return True

    def is_active(self):
        return self.is_enabled

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def gen_confirmation_token(self, expires_in=3600):
        s = Serializer(app.config.get('SECRET_KEY'), expires_in=expires_in)
        token = s.dump({'user_id': self.id})
        return token

    def confirm_token(self, token):
        s = Serializer(app.config.get('SECRET_KEY'))
        token = s.loads(token)
        return token.get('user_id') == self.id

    def user_context(self):
        return dict(id=self.id, email=self.email, first_name=self.first_name,
            last_name=self.last_name, bio=self.bio)

    def get_avatar_url(self):
        url = "https://avatars.io"
        if self.ig_handle is not None:
            return "{}/instagram/{}".format(url, self.ig_handle)
        return url_for("static", filename="default_avatar.jpg")

    def subscribe(self, publication):
        # TODO: build many-many model of subscriptions between users and topics/sources
        pass


class UserAuth(db.Model):
    """
    User authentication abstraction. Separated from user profile model to ensure
    that authentication object data is not exposed to front end of the application.
    Only the user profile model is exposed.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))

    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')

    # Relationships
    user = db.relationship('User', uselist=False, foreign_keys=user_id)

    @classmethod
    def create_user(cls, user_auth_data, user_data):
        try:
            new_user_auth = cls(**user_auth_data)
            new_user_auth._set_password(new_user_auth.password) # hash_password
            new_user = User(**user_data) # create the associated user profile
            new_user_auth.user = new_user # link user profile with user auth

            db.session.add(new_user) # add both to the database
            db.session.add(new_user_auth)
            db.session.commit()
        except Exception as e:
            db.session.rollback() # if any of the above operations fail, rollback everything
            raise e
        return new_user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user is not None and user._verify_password(password):
            return user.user # Return the User model not UserAuth model

    @classmethod
    def validate_new_user(cls, user_auth_data):
        # Verify username does not already exist
        username = user_auth_data.get('username')
        return cls.query.filter_by(username=username).first() is None

    def _set_password(self, password):
        self.password = generate_password_hash(password)

    def _verify_password(self, password):
        return check_password_hash(self.password, password)
