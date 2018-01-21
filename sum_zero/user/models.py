from flask import url_for
from hashlib import md5
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sum_zero import app, db
from sum_zero.summary.models import Bookmark, Comment, Subscription
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
    # Relationships
    subscriptions = db.relationship('Subscription', foreign_keys=[Subscription.user_id],
        backref=db.backref('user', lazy='joined'), lazy='dynamic',
        cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', foreign_keys=[Bookmark.user_id],
        backref=db.backref('user', lazy='joined'), lazy='dynamic',
        cascade='all, delete-orphan')
    comments = db.relationship('Comment', foreign_keys=[Comment.user_id],
        backref=db.backref('user', lazy='joined'), lazy='dynamic',
        cascade='all, delete-orphan')

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

    def has_bookmarked(self, summary_id):
        return self.bookmarks\
            .filter_by(summary_id=summary_id).first() is not None

    def bookmark(self, summary_id):
        bookmark = Bookmark(summary_id=summary_id, user_id=self.id)
        db.session.add(bookmark)
        db.session.commit()

    def del_bookmark(self, summary_id):
        bookmark = self.bookmarks.filter_by(summary_id=summary_id).first()
        db.session.delete(bookmark)
        db.session.commit()

    def is_subscribed(self, source_id):
        return self.subscriptions\
            .filter_by(source_id=source_id).first() is not None

    def subscribe(self, source_id):
        subscription = Subscription(source_id=source_id, user_id=self.id)
        db.session.add(subscription)
        db.session.commit()

    def unsubscribe(self, source_id):
        subscription = self.subscriptions.filter_by(source_id=source_id).first()
        db.session.delete(subscription)
        db.session.commit()


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
