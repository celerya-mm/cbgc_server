from datetime import datetime
from app.app import db


class Administrator(db.Model):
    # Table
    __tablename__ = 'administrators'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(40), index=False, unique=True, nullable=False)
    password = db.Column(db.String(64), index=False, unique=False, nullable=False)
    name = db.Column(db.String(25), index=False, unique=False, nullable=False)
    last_name = db.Column(db.String(25), index=False, unique=False, nullable=False)
    email = db.Column(db.String(80), index=False, unique=True, nullable=False)

    auth_token = db.relationship('AuthToken', backref='administrator')
    event = db.relationship('EventDB', backref='administrator')

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr(self):
        return '<Administrator {}>'.format(self.username)

    def __init__(self, username, password, name, last_name, email, updated_at):
        self.username = username
        self.password = password
        self.email = email
        self.name = name
        self.last_name = last_name
        self.created_at = datetime.now()
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
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
    name = db.Column(db.String(25), index=False, unique=False, nullable=False)
    last_name = db.Column(db.String(25), index=False, unique=False, nullable=False)
    email = db.Column(db.String(80), index=False, unique=True, nullable=False)

    farmer = db.relationship('Farmer', backref='user')
    buyer = db.relationship('Buyer', backref='user')
    auth_token = db.relationship('AuthToken', backref='user')
    event = db.relationship('EventDB', backref='user')

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr(self):
        return '<User {}>'.format(self.username)

    def __init__(self, username, password, name, last_name, email, updated_at):
        self.username = username
        self.password = password
        self.name = name
        self.last_name = last_name
        self.email = email
        self.created_at = datetime.now()
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S")
        }
