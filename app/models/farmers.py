from datetime import datetime

from app.app import db

# importazioni per relazioni "backref"
from .events_db import EventDB  # noqa


class Farmer(db.Model):
	# Table
	__tablename__ = 'farmers'
	# Columns
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	farmer_name = db.Column(db.String(100), index=False, unique=True, nullable=False)

	email = db.Column(db.String(80), index=False, unique=False, nullable=True)
	phone = db.Column(db.String(80), index=False, unique=False, nullable=True)

	address = db.Column(db.String(150), index=False, unique=False, nullable=True)
	cap = db.Column(db.String(5), index=False, unique=False, nullable=True)
	city = db.Column(db.String(55), index=False, unique=False, nullable=True)
	full_address = db.Column(db.String(255), index=False, unique=False, nullable=True)
	coordinates = db.Column(db.String(100), index=False, unique=False, nullable=True)

	affiliation_start_date = db.Column(db.Date, index=False, nullable=True)
	affiliation_end_date = db.Column(db.Date, index=False, nullable=True)
	affiliation_status = db.Column(db.Boolean, index=True, nullable=True)

	stable_code = db.Column(db.String(25), index=False, unique=False, nullable=True)
	stable_type = db.Column(db.String(25), index=False, unique=False, nullable=True)
	stable_productive_orientation = db.Column(db.String(25), index=False, unique=False, nullable=True)
	stable_breeding_methods = db.Column(db.String(25), index=False, unique=False, nullable=True)

	heads = db.relationship('Head', backref='farmer', lazy='dynamic')
	dna_certs = db.relationship('CertificateDna', backref='farmer', lazy='dynamic')
	cons_certs = db.relationship('CertificateCons', backref='farmer', lazy='dynamic')

	events = db.relationship('EventDB', backref='farmer', lazy='dynamic')

	note = db.Column(db.String(255), index=False, unique=False, nullable=True)

	created_at = db.Column(db.DateTime, index=False, nullable=False)
	updated_at = db.Column(db.DateTime, index=False, nullable=False)

	def __repr__(self):
		return f'<ALLEVATORE: {self.farmer_name.data}>'

	def __str__(self):
		return f'<ALLEVATORE: {self.farmer_name.data}>'

	def __init__(self, farmer_name, email, phone=None, address=None, cap=None, city=None, stable_code=None,
	             stable_type=None, stable_productive_orientation=None, stable_breeding_methods=None,
	             affiliation_start_date=None, affiliation_end_date=None, affiliation_status=None,
	             heads=None, dna_certs=None, cons_certs=None, coordinates=None, events=None, note=None):

		from app.utilitys.functions import address_mount, str_to_date, status_true_false

		self.farmer_name = farmer_name

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

		self.stable_code = stable_code or None
		self.stable_type = stable_type or None
		self.stable_productive_orientation = stable_productive_orientation or None
		self.stable_breeding_methods = stable_breeding_methods or None

		self.heads = heads or []
		self.dna_certs = dna_certs or []
		self.cons_certs = cons_certs or []

		self.events = events or []

		self.note = note or None

		self.created_at = datetime.now()
		self.updated_at = datetime.now()

	def create(self):
		"""Crea un nuovo record e lo salva nel db."""
		db.session.add(self)
		db.session.commit()

	def update(_id, data):  # noqa
		"""Salva le modifiche a un record."""
		Farmer.query.filter_by(id=_id).update(data)
		db.session.commit()

	def to_dict(self):
		"""Esporta in un dict la classe."""
		from app.utilitys.functions import date_to_str, status_si_no

		return {
			'id': self.id,
			'farmer_name': self.farmer_name,

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

			'stable_code': self.stable_code,
			'stable_type': self.stable_type,
			'stable_productive_orientation': self.stable_productive_orientation,
			'stable_breeding_methods': self.stable_breeding_methods,

			'note': self.note,

			'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S.%f"),
			'updated_at': date_to_str(self.updated_at, "%Y-%m-%d %H:%M:%S.%f"),
		}
