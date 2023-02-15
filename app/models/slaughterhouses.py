from datetime import datetime

from ..app import db


class Slaughterhouse(db.Model):
	# Table
	__tablename__ = 'slaughterhouses'
	# Columns
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	slaughterhouse = db.Column(db.String(100), index=False, unique=True, nullable=False)
	slaughterhouse_code = db.Column(db.String(20), index=False, unique=True, nullable=True)

	email = db.Column(db.String(80), index=False, unique=False, nullable=True)
	phone = db.Column(db.String(80), index=False, unique=False, nullable=True)

	address = db.Column(db.String(150), index=False, unique=False, nullable=True)
	cap = db.Column(db.String(5), index=False, unique=False, nullable=True)
	city = db.Column(db.String(55), index=False, unique=False, nullable=True)
	full_address = db.Column(db.String(55), index=False, unique=False, nullable=True)
	coordinates = db.Column(db.String(100), index=False, unique=False, nullable=True)

	affiliation_start_date = db.Column(db.DateTime, index=False, nullable=True)
	affiliation_end_date = db.Column(db.DateTime, index=False, nullable=True)
	affiliation_status = db.Column(db.Boolean, index=True, nullable=True)

	note = db.Column(db.String(255), index=False, unique=False, nullable=True)

	cons_cert = db.relationship('CertificateCons', backref='slaughterhouse', lazy='dynamic')

	events = db.relationship('EventDB', backref='slaughterhouse', lazy='dynamic')

	created_at = db.Column(db.DateTime, index=False, nullable=False)
	updated_at = db.Column(db.DateTime, index=False, nullable=False)

	def __repr__(self):
		return f'<MACELLO: {self.farmer_name}>'

	def __str__(self):
		return f'<MACELLO: {self.farmer_name}>'

	def __init__(self, slaughterhouse, slaughterhouse_code, email, phone, address, cap, city,
	             affiliation_start_date, affiliation_status, note, affiliation_end_date=None,
	             cons_cert=None, events=None, coordinates=None):
		from ..utilitys.functions import address_mount, str_to_date, status_true_false

		self.slaughterhouse = slaughterhouse
		self.slaughterhouse_code = slaughterhouse_code

		self.email = email or None
		self.phone = phone or None

		self.address = address or None
		self.cap = cap or None
		self.city = city or None
		self.full_address = address_mount(address, cap, city)
		self.coordinates = coordinates

		self.affiliation_start_date = str_to_date(affiliation_start_date)
		self.affiliation_end_date = str_to_date(affiliation_end_date)
		self.affiliation_status = status_true_false(affiliation_status)

		self.cons_cert = cons_cert or []
		self.events = events or []

		self.note = note or None

		self.created_at = datetime.now()
		self.updated_at = datetime.now()

	def create(self):
		"""Crea un nuovo record e lo salva nel db."""
		db.session.add(self)
		db.session.commit()

	def update():  # noqa
		"""Salva le modifiche a un record."""
		db.session.commit()

	def to_dict(self):
		"""Esporta in un dict la classe."""
		from ..utilitys.functions import date_to_str, status_si_no
		return {
			'id': self.id,
			'slaughterhouse': self.slaughterhouse,
			'slaughterhouse_code': self.slaughterhouse_code,

			'email': self.email,
			'phone': self.phone,

			'address': self.address,
			'cap': self.cap,
			'city': self.city,
			'full_address': self.full_address,
			'coordinates': self.coordinates,

			'affiliation_start_date': date_to_str(self.affiliation_start_date),
			'affiliation_end_date': date_to_str(self.affiliation_end_date),
			'affiliation_status': status_si_no(self.affiliation_status),

			'note': self.note,

			'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S.%f"),
			'updated_at': date_to_str(self.updated_at, "%Y-%m-%d %H:%M:%S.%f"),
		}
