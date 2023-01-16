from datetime import datetime

from app.app import db
from app.utility.functions import address_mount


class Slaughterhouse(db.Model):
    # Table
    __tablename__ = 'slaughterhouses'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slaughterhouse = db.Column(db.String(100), index=False, unique=True, nullable=False)
    slaughterhouse_code = db.Column(db.String(20), index=False, unique=True, nullable=True)

    email = db.Column(db.String(80), index=False, unique=False, nullable=True)
    phone = db.Column(db.String(80), index=False, unique=False, nullable=True)

    address = db.Column(db.String(255), index=False, unique=False, nullable=True)
    cap = db.Column(db.String(5), index=False, unique=False, nullable=True)
    city = db.Column(db.String(55), index=False, unique=False, nullable=True)
    full_address = db.Column(db.String(55), index=False, unique=False, nullable=True)

    affiliation_start_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_end_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_status = db.Column(db.Boolean, index=True, nullable=True)

    note_certificate = db.Column(db.String(255), index=False, unique=False, nullable=True)
    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    head = db.relationship('Head', backref='slaughterhouse')
    cons_cert = db.relationship('CertificateCons', backref='slaughterhouse')
    event = db.relationship('EventDB', backref='slaughterhouse')

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<Slaughterhouse: {}>'.format(self.farmer_name)

    def __init__(self, slaughterhouse, slaughterhouse_code, email, phone, address, cap, city,
                 affiliation_start_date, affiliation_end_date, affiliation_status, note_certificate, note,
                 head=None, cons_cert=None, event=None, updated_at=datetime.now()):

        self.slaughterhouse = slaughterhouse
        self.slaughterhouse_code = slaughterhouse_code

        self.email = email
        self.phone = phone

        self.address = address
        self.cap = cap
        self.city = city
        self.full_address = address_mount(address, cap, city)

        self.affiliation_start_date = affiliation_start_date
        self.affiliation_end_date = affiliation_end_date
        self.affiliation_status = affiliation_status

        if head is None:
            head = []
        self.head = head

        if cons_cert is None:
            cons_cert = []
        self.cons_cert = cons_cert

        if event is None:
            event = []
        self.event = event

        self.note_certificate = note_certificate
        self.note = note

        self.created_at = datetime.now()
        self.updated_at = updated_at

    def to_dict(self):
        if self.affiliation_start_date:
            self.affiliation_start_date = datetime.strftime(self.affiliation_start_date, "%Y-%m-%d")
        if self.affiliation_end_date:
            self.affiliation_end_date = datetime.strftime(self.affiliation_end_date, "%Y-%m-%d")
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

            'affiliation_start_date': self.affiliation_start_date,
            'affiliation_end_date': self.affiliation_end_date,
            'affiliation_status': self.affiliation_status,

            'note_certificate': self.note_certificate,
            'note': self.note,

            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }
