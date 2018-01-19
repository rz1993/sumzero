from datetime import datetime
from sum_zero import db


summary_tag = db.Table('summary_tag',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id', ondelete='CASCADE')),
    db.Column('summary_id', db.Integer, db.ForeignKey('summary.id', ondelete='CASCADE'))
)

class Subscription(db.Model):
    source_id = db.Column(db.Integer,
        db.ForeignKey('source.id', ondelete='CASCADE'), primary_key=True)
    user_id = db.Column(db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Bookmark(db.Model):
    summary_id = db.Column(db.Integer,
        db.ForeignKey('summary.id', ondelete='CASCADE'), primary_key=True)
    user_id = db.Column(db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    body = db.Column(db.Text(), nullable=False)
    published_date = db.Column(db.DateTime())
    source_id = db.Column(db.Integer, db.ForeignKey('source.id', ondelete='CASCADE'))
    link = db.Column(db.String(128))

    tags = db.relationship('Tag', secondary=summary_tag,
        backref=db.backref('summaries', lazy='dynamic'), lazy='dynamic')

    def get_thumbnail(self):
        pass

    def set_tags(self, tags):
        if not isinstance(tags, list):
            tags=[tags]
        for t in tags:
            self.tags.append(t)
            db.session.add(self)
        db.session.commit()

class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    summaries = db.relationship('Summary', backref='source',
        lazy='dynamic')
    subscribers = db.relationship('Subscription', foreign_keys=[Subscription.source_id],
        backref=db.backref('source', lazy='joined'), lazy='dynamic',
        cascade='all, delete-orphan')

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(32), nullable=False)
