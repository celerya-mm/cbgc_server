from datetime import datetime
from app.app import db


class Slaughterhouse(db.Model):
    # Table
    __tablename__ = 'slaughterhouses'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slaughterhouse = db.Column(db.String(100), index=False, unique=True, nullable=False)
    email = db.Column(db.String(80), index=False, unique=False, nullable=True)
    phone = db.Column(db.String(80), index=False, unique=False, nullable=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    affiliation_start_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_end_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_status = db.Column(db.Boolean, index=True, nullable=True)
    note = db.Column(db.String(255), index=False, unique=False, nullable=True)
    address = db.Column(db.String(255), index=False, unique=False, nullable=True)
    cap = db.Column(db.String(5), index=False, unique=False, nullable=True)
    city = db.Column(db.String(55), index=False, unique=False, nullable=True)

    head = db.relationship('Head', backref='slaughterhouse')
    cons_cert = db.relationship('CertificateCons', backref='slaughterhouse')

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr(self):
        return '<Slaughterhouse {}>'.format(self.farmer_name)

    def __init__(self, slaughterhouse, email, phone, address, cap, city, affiliation_start_date, affiliation_end_date,
                 affiliation_status, note, head, cons_cert, created_at, updated_at):
        self.slaughterhouse = slaughterhouse
        self.email = email
        self.phone = phone
        self.address = address
        self.cap = cap
        self.city = city
        self.affiliation_start_date = affiliation_start_date
        self.affiliation_end_date = affiliation_end_date
        self.affiliation_status = affiliation_status
        self.note = note
        self.head = head
        self.cons_cert = cons_cert
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        if self.affiliation_start_date:
            self.affiliation_start_date = datetime.strftime(self.affiliation_start_date, "%Y-%m-%d")
        if self.affiliation_end_date:
            self.affiliation_end_date = datetime.strftime(self.affiliation_end_date, "%Y-%m-%d")
        return {
            'id': self.id,
            'slaughterhouse': self.slaughterhouse,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'cap': self.cap,
            'city': self.city,
            'affiliation_start_date': self.affiliation_start_date,
            'affiliation_end_date': self.affiliation_end_date,
            'affiliation_status': self.affiliation_status,
            'note': self.note,
            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }
