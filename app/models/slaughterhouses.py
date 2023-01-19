from datetime import datetime

from ..app import db

# importazioni per relazioni "ForeignKey"


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

    affiliation_start_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_end_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_status = db.Column(db.Boolean, index=True, nullable=True)

    note_certificate = db.Column(db.String(255), index=False, unique=False, nullable=True)
    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    head = db.relationship('Head', backref='slaughterhouse')
    cons_cert = db.relationship('CertificateCons', backref='slaughterhouse')
    events = db.relationship('EventDB', backref='slaughterhouse')

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<Slaughterhouse: {}>'.format(self.farmer_name)

    def __init__(self, slaughterhouse, slaughterhouse_code, email, phone, address, cap, city,
                 affiliation_start_date, affiliation_status, note_certificate, note, affiliation_end_date=None,
                 head=None, cons_cert=None, events=None, updated_at=datetime.now()):

        from ..utilitys.functions import address_mount, str_to_date

        self.slaughterhouse = slaughterhouse
        self.slaughterhouse_code = slaughterhouse_code

        self.email = email
        self.phone = phone

        self.address = address
        self.cap = cap
        self.city = city
        self.full_address = address_mount(address, cap, city)

        self.affiliation_start_date = str_to_date(affiliation_start_date)
        self.affiliation_end_date = str_to_date(affiliation_end_date)
        self.affiliation_status = affiliation_status

        self.head = head or []
        self.cons_cert = cons_cert or []
        self.events = events or []

        self.note_certificate = note_certificate
        self.note = note

        self.created_at = datetime.now()
        self.updated_at = updated_at

    def to_dict(self):
        """Esporta in un dict la classe."""
        from ..utilitys.functions import date_to_str
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

            'affiliation_start_date': date_to_str(self.affiliation_start_date),
            'affiliation_end_date': date_to_str(self.affiliation_end_date),
            'affiliation_status': self.affiliation_status,

            'note_certificate': self.note_certificate,
            'note': self.note,

            'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': date_to_str(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }
