from app.app import db


class Administrator(db.Model):
    # Table
    __tablename__ = 'administrators'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(40), index=False, unique=True, nullable=False)
    password = db.Column(db.String(64), index=False, unique=False, nullable=False)
    email = db.Column(db.String(80), index=False, unique=True, nullable=False)

    auth_token = db.relationship('AuthToken', backref='administrator')

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr(self):
        return '<Administrator {}>'.format(self.username)

    def __init__(self, username, password, email, created_at, updated_at):
        self.username = username
        self.username = password
        self.email = email
        # self.auth_token = auth_token
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }


class User(db.Model):
    # Table
    __tablename__ = 'users'
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=False, unique=True, nullable=False)
    password = db.Column(db.String(64), index=False, unique=False, nullable=False)
    email = db.Column(db.String(80), index=False, unique=True, nullable=False)

    farmer = db.relationship('Farmer', backref='farmer')
    buyer = db.relationship('Buyer', backref='buyer')
    # slaughterhouse = db.relationship('Slaughterhouse', backref='slaughterhouse')
    auth_token = db.relationship('AuthToken', backref='user')

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr(self):
        return '<User {}>'.format(self.username)

    def __init__(self, username, password, email, created_at, updated_at):
        self.username = username
        self.password = password
        self.email = email
        # self.farmer = farmer
        # self.buyer = buyer
        # self.auth_token = auth_token
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }
