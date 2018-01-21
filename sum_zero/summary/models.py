from datetime import datetime
from sum_zero import db
from sum_zero import utils
from sum_zero.summary import constants as SUMMARY


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
    comments = db.relationship('Comment', backref='summary', lazy='dynamic')

    def add_comment(self, body, user_id, parent_id=None):
        if parent_id is None:
            comment = Comment(user_id=user_id,
                summary_id=self.id,
                body=body)
        else:
            comment = Comment(user_id=user_id,
                summary_id=self.id,
                body=body,
                parent_id=parent_id)
        db.session.add(comment)
        db.session.commit()
        comment.set_depth() # Set the depth after parent has been established
        return comment

    def get_comments(self, order_by='timestamp'):
        """
        Get all top level comments for this summary.
        """
        return self.comments.filter_by(depth=1)\
            .order_by(db.desc(Comment.created_on)).all()

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

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    created_on = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    depth = db.Column(db.SmallInteger, nullable=False, default=1)
    disabled = db.Column(db.Boolean(), default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    summary_id = db.Column(db.Integer, db.ForeignKey('summary.id', ondelete='CASCADE'))
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'))
    children = db.relationship('Comment',
        backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def set_depth(self):
        if self.parent:
            self.depth = self.parent.depth + 1
            db.session.add(self)
            db.session.commit()

    def get_margin(self):
        """
        Comments will be indented based on their depth.
        """
        return SUMMARY.MARGIN * self.depth

    def get_comments(self, order_by='timestamp'):
        return self.children.order_by(db.desc(Comment.created_on)).all()

    def pretty_date(self):
        return utils.pretty_date(self.created_on)
