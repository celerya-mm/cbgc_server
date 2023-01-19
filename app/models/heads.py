from datetime import datetime

from app.app import db
from app.utilitys.functions import year_extract


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
    castration_compliance = db.Column(db.Boolean, index=False, nullable=True)  # True if days (castration-bird) < 240

    slaughter_date = db.Column(db.DateTime, index=False, nullable=True)
    sale_date = db.Column(db.DateTime, index=False, nullable=True)
    sale_year = db.Column(db.Integer, index=False, nullable=True)

    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=True)
    slaughterhouse_id = db.Column(db.Integer, db.ForeignKey('slaughterhouses.id'), nullable=True)

    dna_cert = db.relationship('CertificateDna', backref='head')
    cons_cert = db.relationship('CertificateCons', backref='head')
    event = db.relationship('EventDB', backref='head')

    note_certificate = db.Column(db.String(255), index=False, unique=False, nullable=True)
    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<Head: {}>'.format(self.headset)

    def __init__(self, headset, birth_date, castration_date=None, slaughter_date=None,
                 sale_date=None, note_certificato=None, farmer_id=None, buyer_id=None, slaughterhouse_id=None,
                 dna_certs=None, cons_certs=None, events=None, note=None, updated_at=datetime.now()):

        self.headset = headset

        self.birth_date = birth_date
        self.birth_year = year_extract(birth_date)

        self.castration_date = castration_date
        self.castration_year = year_extract(castration_date)
        self.castration_compliance = compliance(birth_date, castration_date)

        self.slaughter_date = slaughter_date

        self.sale_date = sale_date
        self.sale_year = year_extract(sale_date)

        self.farmer_id = farmer_id
        self.buyer_id = buyer_id
        self.slaughterhouse_id = slaughterhouse_id

        if dna_certs is None:
            dna_certs = []
        self.dna_certs = dna_certs

        if cons_certs is None:
            cons_certs = []
        self.cons_certs = cons_certs

        if events is None:
            events = []
        self.events = events

        self.note_certificate = note_certificato
        self.note = note

        self.created_at = datetime.now()
        self.updated_at = updated_at

    def to_dict(self):
        """Esporta in un dict la classe."""
        if self.birth_date in ["", None] or isinstance(self.birth_date, str):
            pass
        else:
            self.birth_date = datetime.strftime(self.birth_date, "%Y-%m-%d")

        if self.castration_date in ["", None] or isinstance(self.castration_date, str):
            pass
        else:
            self.castration_date = datetime.strftime(self.castration_date, "%Y-%m-%d")

        if self.slaughter_date in ["", None] or isinstance(self.slaughter_date, str):
            pass
        else:
            self.slaughter_date = datetime.strftime(self.slaughter_date, "%Y-%m-%d")

        if self.sale_date in ["", None] or isinstance(self.sale_date, str):
            pass
        else:
            self.sale_date = datetime.strftime(self.sale_date, "%Y-%m-%d")

        return {
            'id': self.id,
            'headset': self.headset,

            'birth_date': self.birth_date,
            'birth_year': self.birth_year,

            'castration_date': self.castration_date,
            'castration_year': self.castration_year,
            'castration_compliance': self.castration_compliance,

            'slaughter_date': self.slaughter_date,
            'sale_date': self.sale_date,
            'sale_year': self.sale_year,

            'farmer_id': self.farmer_id,
            'buyer_id': self.buyer_id,
            'slaughterhouse_id': self.slaughterhouse_id,

            'note_certificate': self.note_certificate,
            'note': self.note,

            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }
