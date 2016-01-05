import datetime
import hashlib
import re
import urllib.parse

from app import bcrypt, db, login_manager


def slugify(title):
    return re.sub('[^\w]+', '-', title).lower()


entry_tags = db.Table(
    'entry_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('entry_id', db.Integer, db.ForeignKey('entry.id')),
)


class Entry(db.Model):
    STATUS_PUBLIC = 0
    STATUS_DRAFT = 1
    STATUS_DELETED = 2

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    slug = db.Column(db.String(100), unique=True)
    body = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=STATUS_PUBLIC)
    created_timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    modified_timestamp = db.Column(
        db.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    tags = db.relationship(
        'Tag',
        secondary=entry_tags,
        backref=db.backref('entries', lazy='dynamic')
    )

    comments = db.relationship('Comment', backref='entry', lazy='dynamic')

    @property
    def tag_list(self):
        return ', '.join(tag.name for tag in self.tags)

    @property
    def tease(self):
        return self.body[:100]

    def __init__(self, *args, **kwargs):
        super(Entry, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        self.slug = ''
        if self.title:
            self.slug = slugify(self.title)

    def __repr__(self):
        return '<Entry: {}>'.format(self.title)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    slug = db.Column(db.String(64), unique=True)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.slug = slugify(self.name)

    def __repr__(self):
        return '<Tag: {}>'.format(self.name)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(255))
    name = db.Column(db.String(64))
    slug = db.Column(db.String(64), unique=True)
    active = db.Column(db.Boolean, default=True)
    created_timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    entries = db.relationship('Entry', backref='author', lazy='dynamic')
    admin = db.Column(db.Boolean, default=False)

    def is_admin(self):
        return self.admin

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.generate_slug()

    def __repr__(self):
        return '<User: {}>'.format(self.name)

    def generate_slug(self):
        if self.name:
            self.slug = slugify(self.name)

    # Flask-Login interface...

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    # Bcrypt-related

    @staticmethod
    def make_password(plaintext):
        return bcrypt.generate_password_hash(plaintext)

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    @classmethod
    def create(cls, email, password, **kwargs):
        return User(
            email=email,
            password_hash=User.make_password(password),
            **kwargs
        )

    @staticmethod
    def authenticate(email, password):
        user = User.query.filter(User.email == email).first()
        if user and user.check_password(password):
            return user
        return False


class Comment(db.Model):
    STATUS_PENDING_MODERATION = 0
    STATUS_PUBLIC = 1
    STATUS_SPAM = 8
    STATUS_DELETED = 9

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    url = db.Column(db.String(100))
    ip_address = db.Column(db.String(64))
    body = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=STATUS_PUBLIC)
    created_timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'))

    def gravatar(self, size=75):
        encoded_email = self.email.encode('utf-8')
        print(encoded_email)
        return 'http://www.gravatar.com/avatar.php?{}'.format(
                urllib.parse.urlencode({
                    'gravatar_id': hashlib.md5(encoded_email).hexdigest(),
                    'size': str(size),
                }))

    def __repr__(self):
        return '<Comment from {}>'.format(self.name)


@login_manager.user_loader
def _user_loader(user_id):
    return User.query.get(int(user_id))
