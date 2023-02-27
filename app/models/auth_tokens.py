from datetime import datetime

from app.app import db


class AuthToken(db.Model):
	# Table
	__tablename__ = 'auth_tokens'
	# Columns
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	token = db.Column(db.String(36), nullable=False, unique=True)
	admin_id = db.Column(db.Integer, db.ForeignKey('administrators.id', ondelete='CASCADE'), nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)

	created_at = db.Column(db.DateTime, index=False, nullable=False)
	expires_at = db.Column(db.DateTime, index=False, nullable=False)

	def __repr__(self):
		return f'<AuthToken: {self.id} - {self.token}>'

	def __str__(self):
		return f'<AuthToken: {self.id} - {self.token}>'

	def __init__(self, token, admin_id=None, user_id=None, expires_at=None):
		self.token = token
		self.admin_id = admin_id or None
		self.user_id = user_id or None
		self.created_at = datetime.now()
		self.expires_at = expires_at

	def create(self):
		"""Crea un nuovo record e lo salva nel db."""
		db.session.add(self)
		db.session.commit()

	def update():  # noqa
		"""Salva le modifiche a un record."""
		db.session.commit()

	def to_dict(self):
		"""Esporta in un dict la classe."""
		from app.utilitys.functions import date_to_str

		return {
			'id': self.id,
			'token': self.token,

			'admin_id': self.admin_id,
			'user_id': self.user_id,

			'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S.%f"),
			'expires_at': date_to_str(self.expires_at, "%Y-%m-%d %H:%M:%S.%f"),
		}
