from datetime import datetime
from app.app import db


class Buyer(db.Model):
    # Table
    __tablename__ = 'buyers'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buyer_name = db.Column(db.String(100), index=False, unique=True, nullable=False)
    buyer_type = db.Column(db.String(40), index=False, unique=False, nullable=False)

    email = db.Column(db.String(80), index=False, unique=False, nullable=True)
    phone = db.Column(db.String(80), index=False, unique=False, nullable=True)
    address = db.Column(db.String(255), index=False, unique=False, nullable=True)
    cap = db.Column(db.String(5), index=False, unique=False, nullable=True)
    city = db.Column(db.String(55), index=False, unique=False, nullable=True)

    affiliation_start_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_end_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_status = db.Column(db.Boolean, index=True, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    heads = db.relationship('Head', backref='buyer')
    cons_certs = db.relationship('CertificateCons', backref='buyer')
    events = db.relationship('EventDB', backref='buyer')

    note = db.Column(db.String(255), index=False, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<Buyer: {}>'.format(self.buyer_name)

    def __init__(self, buyer_name, buyer_type, email=None, phone=None, address=None, cap=None, city=None,
                 affiliation_start_date=None, affiliation_status=None, affiliation_end_date=None, note=None,
                 updated_at=datetime.now()):
        self.buyer_name = buyer_name
        self.buyer_type = buyer_type

        self.email = email
        self.phone = phone
        self.address = address
        self.cap = cap
        self.city = city

        self.affiliation_start_date = affiliation_start_date
        self.affiliation_end_date = affiliation_end_date
        self.affiliation_status = affiliation_status

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
            'buyer_name': self.buyer_name,
            'buyer_type': self.buyer_type,

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
