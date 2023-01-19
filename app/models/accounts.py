from datetime import datetime

from ..app import db

# importazioni per relazioni "backref"
from .tokens import AuthToken  # noqa
from .buyers import Buyer  # noqa
from .events_db import EventDB  # noqa


class Administrator(db.Model):
    # Table
    __tablename__ = 'administrators'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), index=False, unique=True, nullable=False)
    password = db.Column(db.String(64), index=False, unique=False, nullable=False)  # 64 char for hash code

    name = db.Column(db.String(50), index=False, unique=False, nullable=True)
    last_name = db.Column(db.String(50), index=False, unique=False, nullable=True)
    full_name = db.Column(db.String(101), index=False, unique=False, nullable=True)
    email = db.Column(db.String(80), index=False, unique=True, nullable=True)
    phone = db.Column(db.String(25), index=False, unique=False, nullable=True)

    auth_tokens = db.relationship('AuthToken', backref='administrator')
    events = db.relationship('EventDB', backref='administrator')

    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<Administrator: {}>'.format(self.username)

    def __init__(self, username, password, name=None, last_name=None, phone=None, email=None, auth_tokens=None,
                 events=None, note=None, updated_at=datetime.now()):

        from ..utilitys.functions import mount_full_name

        self.username = username
        self.password = password

        self.name = name
        self.last_name = last_name
        self.full_name = mount_full_name(name, last_name)

        self.phone = phone
        self.email = email

        self.auth_tokens = auth_tokens or []

        self.events = events or []

        self.note = note
        self.created_at = datetime.now()
        self.updated_at = updated_at

    def to_dict(self):
        """Esporta in un dict la classe."""
        return {
            'id': self.id,
            'username': self.username,

            'phone': self.phone,
            'email': self.email,

            'name': self.name,
            'last_name': self.last_name,
            'full_name': self.full_name,

            'note': self.note,
            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S")
        }


class User(db.Model):
    # Table
    __tablename__ = 'users'
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=False, unique=True, nullable=False)
    password = db.Column(db.String(64), index=False, unique=False, nullable=False)  # 64 char for hash code

    name = db.Column(db.String(50), index=False, unique=False, nullable=True)
    last_name = db.Column(db.String(50), index=False, unique=False, nullable=True)
    full_name = db.Column(db.String(101), index=False, unique=False, nullable=True)

    email = db.Column(db.String(80), index=False, unique=True, nullable=True)
    phone = db.Column(db.String(25), index=False, unique=False, nullable=True)

    buyers = db.relationship('Buyer', backref='user')
    auth_tokens = db.relationship('AuthToken', backref='user')
    events = db.relationship('EventDB', backref='user')

    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def __init__(self, username, password, name=None, last_name=None, phone=None, email=None, note=None,
                 buyers=None, auth_tokens=None, events=None, updated_at=datetime.now()):

        from ..utilitys.functions import mount_full_name

        self.username = username
        self.password = password

        self.name = name
        self.last_name = last_name
        self.full_name = mount_full_name(name, last_name)

        self.phone = phone
        self.email = email

        self.buyers = buyers or []
        self.auth_tokens = auth_tokens or []

        self.events = events or []

        self.note = note
        self.created_at = datetime.now()
        self.updated_at = updated_at

    def to_dict(self):
        """Esporta in un dict la classe."""
        return {
            'id': self.id,
            'username': self.username,

            'name': self.name,
            'last_name': self.last_name,
            'full_name': self.full_name,

            'phone': self.phone,
            'email': self.email,

            'note': self.note,
            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S")
        }
