from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

from ..app import db


class EventDB(db.Model):
    # Table
    __tablename__ = 'events_db'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event = db.Column(JSONB, index=True, unique=True, nullable=False)

    admin_id = db.Column(db.Integer, db.ForeignKey('administrators.id', ondelete='CASCADE'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id', ondelete='CASCADE'), nullable=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id', ondelete='CASCADE'), nullable=True)
    slaughterhouse_id = db.Column(db.Integer, db.ForeignKey('slaughterhouses.id', ondelete='CASCADE'), nullable=True)
    head_id = db.Column(db.Integer, db.ForeignKey('heads.id', ondelete='CASCADE'), nullable=True)
    cert_cons_id = db.Column(db.Integer, db.ForeignKey('certificates_cons.id', ondelete='CASCADE'), nullable=True)
    cert_dna_id = db.Column(db.Integer, db.ForeignKey('certificates_dna.id', ondelete='CASCADE'), nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<EVENTO: {}>'.format(self.event)

    def __str__(self):
        return '<EVENTO: {}>'.format(self.event)

    def __init__(self, event, admin_id=None, user_id=None, farmer_id=None, buyer_id=None, slaughterhouse_id=None,
                 head_id=None, cert_cons_id=None, cert_dna_id=None):
        self.event = event

        self.admin_id = admin_id
        self.user_id = user_id
        self.farmer_id = farmer_id
        self.buyer_id = buyer_id
        self.slaughterhouse_id = slaughterhouse_id
        self.head_id = head_id
        self.cert_cons_id = cert_cons_id
        self.cert_dna_id = cert_dna_id

        self.created_at = datetime.now()

    def create(self):
        """Crea un nuovo record e lo salva nel db."""
        db.session.add(self)
        db.session.commit()

    def update():  # noqa
        """Salva le modifiche a un record."""
        db.session.commit()

    def to_dict(self):
        """Esporta in un dict la classe."""
        from ..utilitys.functions import date_to_str
        return {
            'id': self.id,
            'event': self.event,

            'admin_id': self.admin_id,
            'user_id': self.user_id,
            'farmer_id': self.farmer_id,
            'buyer_id': self.buyer_id,
            'slaughterhouse_id': self.slaughterhouse_id,
            'head_id': self.head_id,
            'cert_cons_id': self.cert_cons_id,
            'cert_dna_id': self.cert_dna_id,

            'created_at': date_to_str(self.created_at, "%Y-%m-%d %H:%M:%S.%f"),
        }
