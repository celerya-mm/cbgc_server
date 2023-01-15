from datetime import datetime
from app.app import db


class Administrator(db.Model):
    # Table
    __tablename__ = 'administrators'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(40), index=False, unique=True, nullable=False)
    password = db.Column(db.String(64), index=False, unique=False, nullable=False)

    name = db.Column(db.String(25), index=False, unique=False, nullable=True)
    last_name = db.Column(db.String(25), index=False, unique=False, nullable=True)
    email = db.Column(db.String(80), index=False, unique=True, nullable=True)
    phone = db.Column(db.String(25), index=False, unique=False, nullable=True)

    auth_tokens = db.relationship('AuthToken', backref='administrator')
    events = db.relationship('EventDB', backref='administrator')

    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<Administrator: {}>'.format(self.username)

    def __init__(self, username, password, name=None, last_name=None, phone=None, email=None, note=None,
                 updated_at=datetime.now()):
        self.username = username
        self.password = password

        self.name = name
        self.last_name = last_name
        self.phone = phone
        self.email = email

        self.note = note
        self.created_at = datetime.now()
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,

            'name': self.name,
            'last_name': self.last_name,
            'phone': self.phone,
            'email': self.email,

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
    password = db.Column(db.String(64), index=False, unique=False, nullable=False)

    name = db.Column(db.String(25), index=False, unique=False, nullable=True)
    last_name = db.Column(db.String(25), index=False, unique=False, nullable=True)
    email = db.Column(db.String(80), index=False, unique=True, nullable=True)
    phone = db.Column(db.String(25), index=False, unique=False, nullable=True)

    farmers = db.relationship('Farmer', backref='user')
    buyers = db.relationship('Buyer', backref='user')
    auth_tokens = db.relationship('AuthToken', backref='user')
    events = db.relationship('EventDB', backref='user')

    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def __init__(self, username, password, name=None, last_name=None, phone=None, email=None, note=None,
                 updated_at=datetime.now()):
        self.username = username
        self.password = password

        self.name = name
        self.last_name = last_name
        self.phone = phone
        self.email = email

        self.note = note
        self.created_at = datetime.now()
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,

            'name': self.name,
            'last_name': self.last_name,
            'phone': self.phone,
            'email': self.email,

            'note': self.note,
            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S")
        }
