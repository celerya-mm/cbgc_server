from datetime import datetime

from app.app import db
from app.utilitys.functions import year_extract


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

    head_id = db.Column(db.Integer, db.ForeignKey('heads.id'), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)

    events = db.relationship('EventDB', backref='cert_dna')

    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<DNA Certificate: {}>'.format(self.dna_cert_nr)

    def __init__(self, dna_cert_nr, dna_cert_id, dna_cert_date, head_id, farmer_id, events=None, note=None,
                 updated_at=datetime.now()):

        dna_cert_year = year_extract(dna_cert_date)
        if not dna_cert_nr:
            dna_cert_nr = f"{dna_cert_id}/{dna_cert_year}"

        self.dna_cert_id = dna_cert_id
        self.dna_cert_date = dna_cert_date
        self.dna_cert_year = dna_cert_year
        self.dna_cert_nr = dna_cert_nr

        self.head_id = head_id
        self.farmer_id = farmer_id

        if events is None:
            events = []
        self.events = events

        self.note = note
        self.created_at = datetime.now()
        self.updated_at = updated_at

    def to_dict(self):
        """Esporta in un dict la classe."""
        if self.dna_cert_date in ["", None] or isinstance(self.dna_cert_date, str):
            pass
        else:
            self.dna_cert_date = datetime.strftime(self.dna_cert_date, "%Y-%m-%d")

        return {
            'id': self.id,
            'dna_cert_nr': self.dna_cert_nr,
            'dna_cert_date':  self.dna_cert_date,
            'dna_cert_year': self.dna_cert_year,

            'head_id': self.head_id,
            'farmer_id': self.farmer_id,

            'note': self.note,

            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }
