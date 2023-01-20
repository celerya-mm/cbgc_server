from datetime import datetime, timedelta

from ..app import db


def calc_expiration_token():
    _exp = datetime.now() + timedelta(days=1)
    _exp = _exp.replace(hour=0, minute=0, second=0, microsecond=0)
    return _exp


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

    def __str__(self):
        return '<AuthToken: {}>'.format(self.token)

    def __init__(self, token, admin_id=None, user_id=None):
        self.token = token
        self.admin_id = admin_id
        self.user_id = user_id
        self.created_at = datetime.now()
        self.expires_at = calc_expiration_token()

    def to_dict(self):
        """Esporta in un dict la classe."""
        from ..utilitys.functions import date_to_str
        return {
            'id': self.id,
            'token': self.token,
            'admin_id': self.admin_id,
            'user_id': self.user_id,
            'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S.%f"),
            'expires_at': date_to_str(self.expires_at, "%Y-%m-%d %H:%M:%S.%f"),
        }
