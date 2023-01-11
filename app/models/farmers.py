from app.app import db


class Farmer(db.Model):
    # Table
    __tablename__ = 'farmers'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farmer_name = db.Column(db.String(100), index=False, unique=True, nullable=False)
    email = db.Column(db.String(80), index=False, unique=False, nullable=True)
    phone = db.Column(db.String(80), index=False, unique=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    affiliation_start_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_end_date = db.Column(db.DateTime, index=False, nullable=True)
    affiliation_status = db.Column(db.Boolean, index=True, nullable=True)
    note = db.Column(db.String(255), index=False, unique=False, nullable=True)
    address = db.Column(db.String(255), index=False, unique=False, nullable=True)
    cap = db.Column(db.String(5), index=False, unique=False, nullable=True)
    city = db.Column(db.String(55), index=False, unique=False, nullable=True)

    head = db.relationship('Head', backref='farmer')
    dna_cert = db.relationship('CertificateDna', backref='farmer')
    cons_cert = db.relationship('CertificateCons', backref='farmer')

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr(self):
        return '<Farmer {}>'.format(self.farmer_name)

    def __init__(self, farmer_name, email, phone, address, cap, city, affiliation_start_date, affiliation_end_date,
                 affiliation_status, note, head, dna_cert, cons_cert):
        self.farmer_name = farmer_name
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
        self.dna_cert = dna_cert
        self.cons_cert = cons_cert

    def to_dict(self):
        return {
            'id': self.id,
            'farmer_name': self.farmer_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'cap': self.cap,
            'city': self.city,
            'affiliation_start_date': self.affiliation_start_date,
            'affiliation_end_date': self.affiliation_end_date,
            'affiliation_status': self.affiliation_status,
            'note': self.note,
            # 'head': self.head,
            # 'dna_cert': self.dna_cert,
            # 'cons_cert': self.cons_cert,
        }