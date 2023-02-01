from datetime import datetime, timedelta

from ..app import db


def calc_expiration_token():
	"""Scadenza token per login gestionale."""
	_exp = datetime.now() + timedelta(days=1)
	_exp = _exp.replace(hour=0, minute=0, second=0, microsecond=0)
	return _exp


def calc_exp_token_reset_psw():
	"""Imposta scadenza a 15 min."""
	_exp = datetime.now() + timedelta(minutes=15)
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
		return f'<AuthToken: {self.token}>'

	def __str__(self):
		return f'<AuthToken: {self.token}>'

	def __init__(self, token, admin_id=None, user_id=None, expires_at=calc_expiration_token()):
		self.token = token
		self.admin_id = admin_id or None
		self.user_id = user_id or None
		self.created_at = datetime.now()
		self.expires_at = expires_at

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
