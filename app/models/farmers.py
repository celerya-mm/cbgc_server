from datetime import datetime

from app.app import db
from app.utility.functions import address_mount


class Farmer(db.Model):
    # Table
    __tablename__ = 'farmers'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farmer_name = db.Column(db.String(100), index=False, unique=True, nullable=False)

    email = db.Column(db.String(80), index=False, unique=False, nullable=True)
    phone = db.Column(db.String(80), index=False, unique=False, nullable=True)

    address = db.Column(db.String(255), index=False, unique=False, nullable=True)
    cap = db.Column(db.String(5), index=False, unique=False, nullable=True)
    city = db.Column(db.String(55), index=False, unique=False, nullable=True)
    full_address = db.Column(db.String(55), index=False, unique=False, nullable=True)

    affiliation_start_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_end_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_status = db.Column(db.Boolean, index=True, nullable=True)

    stable_code = db.Column(db.String(25), index=False, unique=False, nullable=True)
    stable_type = db.Column(db.String(25), index=False, unique=False, nullable=True)
    stable_productive_orientation = db.Column(db.String(25), index=False, unique=False, nullable=True)
    stable_breeding_methods = db.Column(db.String(25), index=False, unique=False, nullable=True)

    heads = db.relationship('Head', backref='farmer')
    dna_certs = db.relationship('CertificateDna', backref='farmer')
    cons_certs = db.relationship('CertificateCons', backref='farmer')
    events = db.relationship('EventDB', backref='farmer')

    note_certificate = db.Column(db.String(255), index=False, unique=False, nullable=True)
    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<Farmer: {}>'.format(self.farmer_name)

    def __init__(self, farmer_name, email, phone=None, address=None, cap=None, city=None, stable_code=None,
                 stable_type=None, stable_productive_orientation=None, stable_breeding_methods=None,
                 affiliation_start_date=None, affiliation_end_date=None, affiliation_status=None,
                 heads=None, dna_certs=None, cons_certs=None, events=None, note_certificate=None, note=None,
                 updated_at=datetime.now()):

        self.farmer_name = farmer_name

        self.email = email
        self.phone = phone

        self.address = address
        self.cap = cap
        self.city = city
        self.full_address = address_mount(address, cap, city)

        self.affiliation_start_date = affiliation_start_date
        self.affiliation_end_date = affiliation_end_date
        self.affiliation_status = affiliation_status

        self.stable_code = stable_code
        self.stable_type = stable_type
        self.stable_productive_orientation = stable_productive_orientation
        self.stable_breeding_methods = stable_breeding_methods

        if heads is None:
            heads = []
        self.heads = heads

        if dna_certs is None:
            dna_certs = []
        self.dna_certs = dna_certs

        if cons_certs is None:
            cons_certs = []
        self.cons_certs = cons_certs

        if events is None:
            events = []
        self.events = events

        self.note_certificate = note_certificate
        self.note = note

        self.created_at = datetime.now()
        self.updated_at = updated_at

    def to_dict(self):
        if self.affiliation_start_date:
            try:
                self.affiliation_start_date = datetime.strftime(self.affiliation_start_date, "%Y-%m-%d")
            except:
                pass
        if self.affiliation_end_date:
            try:
                self.affiliation_end_date = datetime.strftime(self.affiliation_end_date, "%Y-%m-%d")
            except:
                pass
        return {
            'id': self.id,
            'farmer_name': self.farmer_name,

            'email': self.email,
            'phone': self.phone,

            'address': self.address,
            'cap': self.cap,
            'city': self.city,
            'full_address': self.full_address,

            'stable_code': self.stable_code,
            'stable_type': self.stable_type,
            'affiliation_end_date': self.affiliation_end_date,
            'affiliation_status': self.affiliation_status,

            'affiliation_start_date': self.affiliation_start_date,
            'stable_productive_orientation': self.stable_productive_orientation,
            'stable_breeding_methods': self.stable_breeding_methods,

            'note_certificate': self.note_certificate,
            'note': self.note,

            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }
