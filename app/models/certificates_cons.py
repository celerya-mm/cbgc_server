from datetime import datetime

from ..app import db

# importazioni per relazioni "ForeignKey"
# from .heads import Head  # noqa
# from .buyers import Buyer  # noqa
# from .farmers import Farmer  # noqa
# from .slaughterhouses import Slaughterhouse  # noqa

# importazioni per relazioni "backref"
from .events_db import EventDB  # noqa


def mount_code(_id, year, var=None):
    """Monta il codice del certificato"""
    if _id and year and var:
        code = f"{_id}{var}/{year}"
    else:
        code = f"{_id}/{year}"
    return code


class CertificateCons(db.Model):
    # Table
    __tablename__ = 'certificates_cons'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    certificate_id = db.Column(db.Integer, index=False, unique=False, nullable=False)
    certificate_var = db.Column(db.String(10), index=False, unique=False, nullable=True)
    certificate_date = db.Column(db.DateTime, index=False, nullable=False)
    certificate_year = db.Column(db.Integer, index=False, nullable=False)

    certificate_nr = db.Column(db.String(50), index=False, unique=True, nullable=False)

    certificate_pdf = db.Column(db.LargeBinary, index=False, nullable=True)

    cockade_id = db.Column(db.Integer, index=False, unique=False, nullable=True)
    cockade_var = db.Column(db.String(10), index=False, unique=False, nullable=True)
    cockade_nr = db.Column(db.String(20), index=False, unique=True, nullable=True)

    sale_type = db.Column(db.String(50), index=False, unique=True, nullable=True)
    sale_quantity = db.Column(db.Float, index=False, nullable=True)
    sale_rest = db.Column(db.Float, index=False, nullable=True)

    invoice_nr = db.Column(db.String(20), index=False, unique=False, nullable=True)
    invoice_date = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    invoice_status = db.Column(db.String(20), index=False, unique=False, nullable=True)

    emitted = db.Column(db.Boolean, index=False, nullable=True)

    head_id = db.Column(db.Integer, db.ForeignKey('heads.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    slaughterhouse_id = db.Column(db.Integer, db.ForeignKey('slaughterhouses.id'), nullable=True)

    events = db.relationship('EventDB', backref='cert_cons')

    note_certificate = db.Column(db.String(255), index=False, unique=False, nullable=True)
    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<CONSORZIO Certificate: {}>'.format(self.headset)

    def __init__(self,
                 certificate_var, certificate_date, certificate_id, certificate_pdf=None,
                 cockade_var=None, cockade_id=None,
                 sale_type=None, sale_quantity=None, sale_rest=None,
                 head_id=None, farmer_id=None, buyer_id=None, slaughterhouse_id=None,
                 invoice_nr=None, invoice_date=None, invoice_status=None,
                 events=None, note_certificate=None, note=None, updated_at=datetime.now()):

        from ..utilitys.functions import year_extract, str_to_date

        self.certificate_id = certificate_id
        self.certificate_var = certificate_var
        self.certificate_date = str_to_date(certificate_date)

        certificate_year = year_extract(certificate_date)
        self.certificate_year = certificate_year

        self.certificate_nr = mount_code(certificate_id, certificate_year, certificate_var)

        self.cockade_id = cockade_id
        self.cockade_var = cockade_var
        self.cockade_nr = mount_code(cockade_id, certificate_year, cockade_var)

        self.sale_type = sale_type
        self.sale_quantity = sale_quantity
        self.sale_rest = sale_rest

        self.head_id = head_id
        self.farmer_id = farmer_id
        self.buyer_id = buyer_id
        self.slaughterhouse_id = slaughterhouse_id

        self.certificate_pdf = certificate_pdf
        self.invoice_nr = invoice_nr
        self.invoice_date = str_to_date(invoice_date)
        self.invoice_status = invoice_status

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
            'certificate_id': self.certificate_id,
            'certificate_var': self.certificate_var,
            'certificate_nr': self.certificate_nr,

            'certificate_date': date_to_str(self.certificate_date),
            'certificate_year': self.certificate_year,

            'cockade_id': self.cockade_id,
            'cockade_var': self.cockade_var,
            'cockade_nr': self.cockade_nr,

            'sale_type': self.sale_type,
            'sale_quantity': self.sale_quantity,
            'sale_rest': self.sale_rest,

            'invoice_nr': self.invoice_nr,
            'invoice_date': date_to_str(self.invoice_date),
            'invoice_status': self.invoice_status,

            'head_id': self.head_id,
            'farmer_id': self.farmer_id,
            'buyer_id': self.buyer_id,
            'slaughterhouse_id': self.slaughterhouse_id,

            'note_certificate': self.note_certificate,
            'note': self.note,

            'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': date_to_str(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }
