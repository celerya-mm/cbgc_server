from datetime import datetime
from dateutil.relativedelta import relativedelta

from ..app import db

# importazioni per relazioni "backref"
from .events_db import EventDB  # noqa
from .certificates_dna import CertificateDna  # noqa
from .certificates_cons import CertificateCons  # noqa


def verify_castration(birth, castration):
    """Verifica conformità castrazione entro gli OTTO mesi."""
    from ..utilitys.functions import str_to_date
    if castration not in [None, "nan", ""] and isinstance(castration, str):
        _max = str_to_date(birth) + relativedelta(months=8)
        return bool(str_to_date(castration) <= _max)
    elif castration is not None and isinstance(castration, datetime):
        _max = birth + relativedelta(months=8)
        return bool(castration <= _max)
    else:
        return None


class Head(db.Model):
    # Table
    __tablename__ = 'heads'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    headset = db.Column(db.String(14), index=False, unique=True, nullable=False)

    birth_date = db.Column(db.DateTime, index=False, nullable=False)
    birth_year = db.Column(db.Integer, index=False, nullable=False)

    castration_date = db.Column(db.DateTime, index=False, nullable=True)
    castration_year = db.Column(db.Integer, index=False, nullable=True)

    # True if (castration_date - castration_date) <= 8 month
    castration_compliance = db.Column(db.Boolean, index=False, nullable=True)

    slaughter_date = db.Column(db.DateTime, index=False, nullable=True)

    sale_date = db.Column(db.DateTime, index=False, nullable=True)
    sale_year = db.Column(db.Integer, index=False, nullable=True)

    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=True)

    dna_cert = db.relationship('CertificateDna', backref='head', lazy=True)
    cons_cert = db.relationship('CertificateCons', backref='head', lazy=True)

    events = db.relationship('EventDB', backref='head', lazy=True)

    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return f'<CAPO: {self.headset}>'

    def __str__(self):
        return f'<CAPO: {self.headset}>'

    def __init__(self, headset, birth_date, castration_date=None, slaughter_date=None, sale_date=None,
                 note_certificate=None, farmer_id=None, dna_cert=None, cons_cert=None, events=None, note=None):
        from ..utilitys.functions import year_extract, str_to_date

        self.headset = headset

        self.birth_date = str_to_date(birth_date)
        self.birth_year = year_extract(birth_date)

        self.castration_date = str_to_date(castration_date)
        self.castration_year = year_extract(castration_date)
        self.castration_compliance = verify_castration(birth_date, castration_date)

        self.slaughter_date = str_to_date(slaughter_date)

        self.sale_date = str_to_date(sale_date)
        self.sale_year = year_extract(sale_date)

        self.farmer_id = farmer_id

        self.dna_cert = dna_cert or []
        self.cons_cert = cons_cert or []

        self.events = events or []

        self.note = note or None

        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self):
        """Esporta in un dict la classe."""
        from ..utilitys.functions import date_to_str
        return {
            'id': self.id,
            'headset': self.headset,

            'birth_date': date_to_str(self.birth_date),
            'birth_year': self.birth_year,

            'castration_date': date_to_str(self.castration_date),
            'castration_year': self.castration_year,
            'castration_compliance': self.castration_compliance,

            'slaughter_date': date_to_str(self.slaughter_date),
            'sale_date': date_to_str(self.sale_date),
            'sale_year': self.sale_year,

            'farmer_id': self.farmer_id,

            'note': self.note,

            'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S.%f"),
            'updated_at': date_to_str(self.updated_at, "%Y-%m-%d %H:%M:%S.%f"),
        }
