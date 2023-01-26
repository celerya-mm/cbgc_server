from datetime import datetime

from ..app import db

# importazioni per relazioni "backref"
from .heads import Head  # noqa
from .certificates_cons import CertificateCons  # noqa
from .events_db import EventDB  # noqa


class Buyer(db.Model):
    # Table
    __tablename__ = 'buyers'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buyer_name = db.Column(db.String(100), index=False, unique=True, nullable=False)
    buyer_type = db.Column(db.String(40), index=False, unique=False, nullable=False)

    email = db.Column(db.String(80), index=False, unique=False, nullable=True)
    phone = db.Column(db.String(80), index=False, unique=False, nullable=True)

    address = db.Column(db.String(150), index=False, unique=False, nullable=True)
    cap = db.Column(db.String(5), index=False, unique=False, nullable=True)
    city = db.Column(db.String(55), index=False, unique=False, nullable=True)
    full_address = db.Column(db.String(255), index=False, unique=False, nullable=True)

    affiliation_start_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_end_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_status = db.Column(db.Boolean, index=True, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    cons_certs = db.relationship('CertificateCons', backref='buyer', lazy=True)
    events = db.relationship('EventDB', backref='buyer', lazy=True)

    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return f'<BUYER ID: {self.id.data}; Rag. Sociale: {self.buyer_name.data}>'

    def __str__(self):
        return f'<BUYER ID: {self.id.data}; Rag. Sociale: {self.buyer_name.data}>'

    def __init__(self, buyer_name, buyer_type, email=None, phone=None, address=None, cap=None, city=None,
                 affiliation_start_date=None, affiliation_status=None, affiliation_end_date=None, user_id=None,
                 cons_certs=None, events=None, note_certificate=None, note=None):
        from ..utilitys.functions import address_mount, str_to_date, status_true_false

        self.buyer_name = buyer_name
        self.buyer_type = buyer_type

        self.email = email
        self.phone = phone

        self.address = address
        self.cap = cap
        self.city = city
        self.full_address = address_mount(address, cap, city)

        self.affiliation_start_date = str_to_date(affiliation_start_date)
        self.affiliation_end_date = str_to_date(affiliation_end_date)
        self.affiliation_status = status_true_false(affiliation_status)

        self.user_id = user_id or None

        self.cons_certs = cons_certs or []
        self.events = events or []

        self.note = note or None

        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self):
        """Esporta in un dict la classe."""
        from ..utilitys.functions import date_to_str, status_si_no
        return {
            'id': self.id,
            'buyer_name': self.buyer_name,
            'buyer_type': self.buyer_type,

            'email': self.email,
            'phone': self.phone,

            'address': self.address,
            'cap': self.cap,
            'city': self.city,
            'full_address': self.full_address,

            'affiliation_start_date': date_to_str(self.affiliation_start_date),
            'affiliation_end_date': date_to_str(self.affiliation_end_date),
            'affiliation_status': status_si_no(self.affiliation_status),

            'note': self.note,

            'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S.%f"),
            'updated_at': date_to_str(self.updated_at, "%Y-%m-%d %H:%M:%S.%f"),
        }
