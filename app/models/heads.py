from datetime import datetime
from dateutil.relativedelta import relativedelta

from ..app import db

# importazioni per relazioni "ForeignKey"
# from .farmers import Farmer  # noqa
# from .buyers import Buyer  # noqa
# from .slaughterhouses import Slaughterhouse  # noqa

# importazioni per relazioni "backref"
from .events_db import EventDB  # noqa
from .certificates_dna import CertificateDna  # noqa
from .certificates_cons import CertificateCons  # noqa


def castration_compliance(birth, castration):
    """Verifica conformità castrazione entro gli OTTO mesi."""
    from ..utilitys.functions import str_to_date, date_to_str
    if castration:
        _max = str_to_date(birth) + relativedelta(month=8)
        print("BIRTH:", date_to_str(birth))
        print("MAX:", _max)
        print("CASTRATION:", date_to_str(castration))
        return bool(str_to_date(castration) <= _max)
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
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=True)
    slaughterhouse_id = db.Column(db.Integer, db.ForeignKey('slaughterhouses.id'), nullable=True)

    dna_cert = db.relationship('CertificateDna', backref='head')
    cons_cert = db.relationship('CertificateCons', backref='head')
    events = db.relationship('EventDB', backref='head')

    note_certificate = db.Column(db.String(255), index=False, unique=False, nullable=True)
    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<Head: {}>'.format(self.headset)

    def __init__(self, headset, birth_date, castration_date=None, slaughter_date=None,
                 sale_date=None, note_certificate=None, farmer_id=None, buyer_id=None, slaughterhouse_id=None,
                 dna_certs=None, cons_certs=None, events=None, note=None, updated_at=datetime.now()):

        from ..utilitys.functions import year_extract, str_to_date

        self.headset = headset

        self.birth_date = str_to_date(birth_date)
        self.birth_year = year_extract(birth_date)

        self.castration_date = str_to_date(castration_date)
        self.castration_year = year_extract(castration_date)
        self.castration_compliance = castration_compliance(birth_date, castration_date)

        self.slaughter_date = str_to_date(slaughter_date)

        self.sale_date = str_to_date(sale_date)
        self.sale_year = year_extract(sale_date)

        self.farmer_id = farmer_id
        self.buyer_id = buyer_id
        self.slaughterhouse_id = slaughterhouse_id

        self.dna_certs = dna_certs or []
        self.cons_certs = cons_certs or []

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
            'buyer_id': self.buyer_id,
            'slaughterhouse_id': self.slaughterhouse_id,

            'note_certificate': self.note_certificate,
            'note': self.note,

            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }
