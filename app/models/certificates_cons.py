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
    cockade_id = db.Column(db.String(20), index=False, unique=True, nullable=True)
    sale_type = db.Column(db.String(50), index=False, unique=True, nullable=True)
    sale_quantity = db.Column(db.Float, index=False, nullable=True)
    certificate_pdf = db.Column(db.LargeBinary, index=False, nullable=True)
    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    head_id = db.Column(db.Integer, db.ForeignKey('heads.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    slaughterhouse_id = db.Column(db.Integer, db.ForeignKey('slaughterhouses.id'), nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr(self):
        return '<CertificateCons {}>'.format(self.headset)

    def __init__(self, certificate_nr, certificate_date, certificate_year, cockade_id, sale_type, sale_quantity, note,
                 head_id, farmer_id, buyer_id, created_at, updated_at):
        self.certificate_nr = certificate_nr
        self.certificate_date = certificate_date
        self.certificate_year = certificate_year
        self.cockade_id = cockade_id
        self.sale_type = sale_type
        self.sale_type = sale_type
        self.sale_quantity = sale_quantity
        self.note = note
        self.head_id = head_id
        self.farmer_id = farmer_id
        self.buyer_id = buyer_id
        self.buyer_id = created_at
        self.buyer_id = updated_at

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
            'note': self.note,
            'head_id': self.head_id,
            'farmer_id': self.farmer_id,
            'buyer_id': self.buyer_id,
            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }
