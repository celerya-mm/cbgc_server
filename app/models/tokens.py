from datetime import datetime

from ..app import db


class AuthToken(db.Model):
    # Table
    __tablename__ = 'auth_tokens'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(36), nullable=False, unique=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('administrators.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    expires_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<AuthToken: {}>'.format(self.token)

    def __init__(self, token, expires_at, admin_id=None, user_id=None):
        self.token = token
        self.expires_at = expires_at
        self.admin_id = admin_id
        self.user_id = user_id
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'admin_id': self.admin_id,
            'user_id': self.user_id,
            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'expires_at': datetime.strftime(self.expires_at, "%Y-%m-%d %H:%M:%S"),
        }
