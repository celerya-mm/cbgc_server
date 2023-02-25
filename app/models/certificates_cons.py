from datetime import datetime

from app.app import db

# importazioni per relazioni "backref"
from .events_db import EventDB  # noqa


def mount_code(_id, year, var=None):
    """Monta il codice del certificato"""
    if _id and year and var:
        code = f"{_id}{var}/{str(year)}"
    elif _id in ["", None]:
        code = None
    else:
        code = f"{_id}/{str(year)}"
    return code


def year_cert_calc():
    """L'anno del certificato va dal 01/07 al 30/06 dell'anno successivo."""
    date = datetime.now()
    month = date.month
    year = date.year
    if month >= 7:
        return year
    else:
        return year - 1


def year_cert_calc_update(date):
    """L'anno del certificato va dal 01/07 al 30/06 dell'anno successivo."""
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")

    month = date.month
    year = date.year
    if month >= 7:
        return year
    else:
        return year - 1


class CertificateCons(db.Model):
    # Table
    __tablename__ = 'certificates_cons'

    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    certificate_id = db.Column(db.Integer, index=False, unique=False, nullable=False)
    certificate_var = db.Column(db.String(10), index=False, unique=False, nullable=True)
    certificate_date = db.Column(db.Date, index=False, nullable=False)
    certificate_year = db.Column(db.Integer, index=False, nullable=False, default=year_cert_calc())

    certificate_nr = db.Column(db.String(50), index=False, unique=True, nullable=False)
    emitted = db.Column(db.Boolean, index=False, nullable=True)

    certificate_pdf = db.Column(db.LargeBinary, index=False, nullable=True)

    cockade_id = db.Column(db.Integer, index=False, unique=False, nullable=True)
    cockade_var = db.Column(db.String(10), index=False, unique=False, nullable=True)
    cockade_nr = db.Column(db.String(20), index=False, unique=True, nullable=True)

    sale_type = db.Column(db.String(50), index=False, unique=False, nullable=True)
    sale_quantity = db.Column(db.Float, index=False, nullable=True)
    sale_rest = db.Column(db.Float, index=False, nullable=True)

    head_category = db.Column(db.String(10), index=False, unique=False, nullable=True)
    head_age = db.Column(db.Integer, index=False, unique=False, nullable=True)
    batch_number = db.Column(db.String(50), index=False, unique=False, nullable=True)

    invoice_nr = db.Column(db.String(20), index=False, unique=False, nullable=True)
    invoice_date = db.Column(db.Date, index=False, unique=False, nullable=True)
    invoice_status = db.Column(db.String(20), index=False, unique=False, nullable=True)

    head_id = db.Column(db.Integer, db.ForeignKey('heads.id', ondelete='CASCADE'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    slaughterhouse_id = db.Column(db.Integer, db.ForeignKey('slaughterhouses.id'), nullable=True)

    events = db.relationship('EventDB', backref='cert_cons', lazy='dynamic')

    note_certificate = db.Column(db.String(255), index=False, unique=False, nullable=True)
    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<CONSORZIO Certificato: {}>'.format(self.headset)

    def __str__(self):
        return '<CONSORZIO Certificato: {}>'.format(self.headset)

    def __init__(self,
                 certificate_var, certificate_date, certificate_id, certificate_pdf=None,
                 cockade_var=None, cockade_id=None, emitted=None,
                 sale_type=None, sale_quantity=None, batch_number=None, head_category=None, head_age=None,
                 head_id=None, farmer_id=None, buyer_id=None, slaughterhouse_id=None,
                 invoice_nr=None, invoice_date=None, invoice_status=None,
                 events=None, note_certificate=None, note=None):
        from ..utilitys.functions import str_to_date, status_true_false

        self.certificate_id = certificate_id
        self.certificate_var = certificate_var or None
        self.certificate_date = str_to_date(certificate_date)

        certificate_year = year_cert_calc()
        self.certificate_year = certificate_year

        self.certificate_nr = mount_code(certificate_id, certificate_year, certificate_var)
        self.emitted = status_true_false(emitted)

        self.cockade_id = cockade_id
        self.cockade_var = cockade_var or None
        self.cockade_nr = mount_code(cockade_id, certificate_year, cockade_var)

        self.sale_type = sale_type or None
        self.sale_quantity = sale_quantity or None
        self.sale_rest = sale_quantity or None

        self.head_category = head_category or None
        self.head_age = head_age or None
        self.batch_number = batch_number or None

        self.certificate_pdf = certificate_pdf or None

        self.invoice_nr = invoice_nr or None
        self.invoice_date = str_to_date(invoice_date)
        self.invoice_status = invoice_status or None

        self.events = events or []

        self.head_id = head_id or []
        self.farmer_id = farmer_id or []
        self.buyer_id = buyer_id or []
        self.slaughterhouse_id = slaughterhouse_id or []

        self.note_certificate = note_certificate or None
        self.note = note

        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def create(self):
        """Crea un nuovo record e lo salva nel db."""
        db.session.add(self)
        db.session.commit()

    def update(_id, data):  # noqa
        """Salva le modifiche a un record."""
        CertificateCons.query.filter_by(id=_id).update(data)
        db.session.commit()

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

            'emitted': self.emitted,

            'cockade_id': self.cockade_id,
            'cockade_var': self.cockade_var,
            'cockade_nr': self.cockade_nr,

            'sale_type': self.sale_type,
            'sale_quantity': self.sale_quantity,
            'sale_rest': self.sale_rest,

            'head_category': self.head_category,
            'head_age': self.head_age,
            'batch_number': self.batch_number,

            'invoice_nr': self.invoice_nr,
            'invoice_date': date_to_str(self.invoice_date),
            'invoice_status': self.invoice_status,

            'head_id': self.head_id,
            'farmer_id': self.farmer_id,
            'buyer_id': self.buyer_id,
            'slaughterhouse_id': self.slaughterhouse_id,

            'note_certificate': self.note_certificate,
            'note': self.note,

            'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S.%f"),
            'updated_at': date_to_str(self.updated_at, "%Y-%m-%d %H:%M:%S.%f"),
        }
