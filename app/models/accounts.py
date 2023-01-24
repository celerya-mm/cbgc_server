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

    auth_tokens = db.relationship('AuthToken', backref='administrator', lazy=True)
    events = db.relationship('EventDB', backref='administrator', lazy=True)

    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return f'<AMMINISTRATORE ID: {self.id}; username: {self.username}>'

    def __str__(self):
        return f'<AMMINISTRATORE ID: {self.id}; username: {self.username}>'

    def __init__(self, username, password=None, name=None, last_name=None, phone=None, email=None, auth_tokens=None,
                 events=None, note=None):
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

        self.note = note or None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self):
        """Esporta in un dict la classe."""
        from ..utilitys.functions import date_to_str
        return {
            'id': self.id,
            'username': self.username,

            'phone': self.phone,
            'email': self.email,

            'name': self.name,
            'last_name': self.last_name,
            'full_name': self.full_name,

            'note': self.note,
            'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S.%f"),
            'updated_at': date_to_str(self.updated_at, "%Y-%m-%d %H:%M:%S.%f")
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

    buyers = db.relationship('Buyer', backref='user', lazy=True)
    auth_tokens = db.relationship('AuthToken', backref='user', lazy=True)
    events = db.relationship('EventDB', backref='user', lazy=True)

    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<UTENTE: {}>'.format(self.username)

    def __str__(self):
        return '<UTENTE: {}>'.format(self.username)

    def __init__(self, username, password=None, name=None, last_name=None, phone=None, email=None, note=None,
                 buyers=None, auth_tokens=None, events=None):
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

        self.note = note or None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self):
        """Esporta in un dict la classe."""
        from ..utilitys.functions import date_to_str
        return {
            'id': self.id,
            'username': self.username,

            'name': self.name,
            'last_name': self.last_name,
            'full_name': self.full_name,

            'phone': self.phone,
            'email': self.email,

            'note': self.note,
            'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S.%f"),
            'updated_at': date_to_str(self.updated_at, "%Y-%m-%d %H:%M:%S.%f")
        }
