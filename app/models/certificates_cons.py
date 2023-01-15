from datetime import datetime
from app.app import db


class CertificateCons(db.Model):
    # Table
    __tablename__ = 'certificates_cons'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    certificate_nr = db.Column(db.String(20), index=False, unique=True, nullable=False)
    certificate_date = db.Column(db.DateTime, index=False, nullable=False)
    certificate_year = db.Column(db.Integer, index=False, nullable=False)
    certificate_pdf = db.Column(db.LargeBinary, index=False, nullable=True)

    cockade_id = db.Column(db.String(20), index=False, unique=True, nullable=True)

    sale_type = db.Column(db.String(50), index=False, unique=True, nullable=True)
    sale_quantity = db.Column(db.Float, index=False, nullable=True)
    sale_rest = db.Column(db.Float, index=False, nullable=True)

    invoice_nr = db.Column(db.String(20), index=False, unique=False, nullable=True)
    invoice_date = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    invoice_type = db.Column(db.String(20), index=False, unique=False, nullable=True)
    invoice_status = db.Column(db.String(20), index=False, unique=False, nullable=True)

    head_id = db.Column(db.Integer, db.ForeignKey('heads.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    slaughterhouse_id = db.Column(db.Integer, db.ForeignKey('slaughterhouses.id'), nullable=True)

    events = db.relationship('EventDB', backref='cert_cons')

    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<CONS Certificate: {}>'.format(self.headset)

    def __init__(self, certificate_nr, certificate_date, certificate_year, cockade_id, sale_type, sale_quantity,
                 sale_rest=None, head_id=None, farmer_id=None, buyer_id=None, slaughterhouse_id=None,
                 certificate_pdf=None, invoice_nr=None, invoice_date=None, invoice_type=None, invoice_status=None,
                 note=None,  updated_at=datetime.now()):
        self.certificate_nr = certificate_nr
        self.certificate_date = certificate_date
        self.certificate_year = certificate_year

        self.cockade_id = cockade_id

        self.sale_type = sale_type
        self.sale_quantity = sale_quantity
        self.sale_rest = sale_rest

        self.head_id = head_id
        self.farmer_id = farmer_id
        self.buyer_id = buyer_id
        self.slaughterhouse_id = slaughterhouse_id

        self.certificate_pdf = certificate_pdf
        self.invoice_nr = invoice_nr
        self.invoice_date = invoice_date
        self.invoice_type = invoice_type
        self.invoice_status = invoice_status

        self.note = note
        self.created_at = datetime.now()
        self.updated_at = updated_at

    def to_dict(self):
        if self.certificate_date:
            self.certificate_date = datetime.strftime(self.certificate_date, "%Y-%m-%d")
        return {
            'id': self.id,
            'certificate_nr': self.certificate_nr,
            'certificate_date': self.certificate_date,
            'certificate_year': self.certificate_year,

            'cockade_id': self.cockade_id,

            'sale_type': self.sale_type,
            'sale_quantity': self.sale_quantity,
            'sale_rest': self.sale_rest,

            'invoice_nr': self.invoice_nr,
            'invoice_date': self.invoice_date,
            'invoice_type': self.invoice_type,
            'invoice_status': self.invoice_status,

            'head_id': self.head_id,
            'farmer_id': self.farmer_id,
            'buyer_id': self.buyer_id,
            'slaughterhouse_id': self.slaughterhouse_id,

            'note': self.note,
            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }
