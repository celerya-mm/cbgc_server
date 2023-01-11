from app.app import db


class AuthToken(db.Model):
    # Table
    __tablename__ = 'auth_tokens'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(64), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, index=False, nullable=False)
    administrator_id = db.Column(db.Integer, db.ForeignKey('administrators.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)

    def __init__(self, token, expires_at, administrator_id, user_id, created_at):
        self.token = token
        self.expires_at = expires_at
        self.administrator_id = administrator_id
        self.user_id = user_id
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'expires_at': self.expires_at,
            'administrator_id': self.administrator_id,
            'user_id': self.user_id,
        }
