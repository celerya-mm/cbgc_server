from datetime import datetime

from ..app import db

# importazioni per relazioni "backref"
from .events_db import EventDB  # noqa


class CertificateDna(db.Model):
    # Table
    __tablename__ = 'certificates_dna'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    dna_cert_id = db.Column(db.String(20), index=False, unique=False, nullable=False)
    dna_cert_date = db.Column(db.DateTime, index=False, nullable=False)
    dna_cert_year = db.Column(db.Integer, index=False, nullable=False)
    dna_cert_nr = db.Column(db.String(20), index=False, unique=True, nullable=False)
    dna_cert_pdf = db.Column(db.LargeBinary, index=False, nullable=True)

    veterinarian = db.Column(db.String(50), index=False, unique=False, nullable=True)

    head_id = db.Column(db.Integer, db.ForeignKey('heads.id', ondelete='CASCADE'), nullable=False, unique=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False, unique=False)

    events = db.relationship('EventDB', backref='cert_dna', lazy='dynamic')

    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<DNA Certificato: {}>'.format(self.dna_cert_nr)

    def __str__(self):
        return '<DNA Certificato: {}>'.format(self.dna_cert_nr)

    def __init__(self, dna_cert_id, dna_cert_date, head_id, farmer_id, veterinarian, note=None):
        from ..utilitys.functions import year_extract, str_to_date

        self.dna_cert_id = dna_cert_id
        self.dna_cert_date = str_to_date(dna_cert_date)
        self.dna_cert_year = year_extract(dna_cert_date)
        self.dna_cert_nr = f"{dna_cert_id}/{self.dna_cert_year}"

        self.veterinarian = veterinarian or None

        self.head_id = head_id or None
        self.farmer_id = farmer_id or None

        self.note = note or None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def create(self):
        """Crea un nuovo record e lo salva nel db."""
        db.session.add(self)
        db.session.commit()

    def update(_id, data):  # noqa
        """Salva le modifiche a un record."""
        CertificateDna.query.filter_by(id=_id).update(data)
        db.session.commit()

    def to_dict(self):
        """Esporta in un dict la classe."""
        from ..utilitys.functions import date_to_str
        return {
            'id': self.id,
            'dna_cert_id': self.dna_cert_id,
            'dna_cert_date': date_to_str(self.dna_cert_date),
            'dna_cert_year': self.dna_cert_year,
            'dna_cert_nr': f"{self.dna_cert_id}/{self.dna_cert_year}",

            'veterinarian': self.veterinarian,

            'head_id': self.head_id,
            'farmer_id': self.farmer_id,

            'note': self.note,

            'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S.%f"),
            'updated_at': date_to_str(self.updated_at, "%Y-%m-%d %H:%M:%S.%f"),
        }
