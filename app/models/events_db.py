from datetime import datetime
from app.app import db
from sqlalchemy.dialects.postgresql import JSON


class EventDB(db.Model):
    # Table
    __tablename__ = 'events_db'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event = db.Column(JSON, index=False, unique=False, nullable=False)

    admin_id = db.Column(db.Integer, db.ForeignKey('administrators.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=True)
    slaughterhouse_id = db.Column(db.Integer, db.ForeignKey('slaughterhouses.id'), nullable=True)
    head_id = db.Column(db.Integer, db.ForeignKey('heads.id'), nullable=True)
    cert_cons_id = db.Column(db.Integer, db.ForeignKey('certificates_cons.id'), nullable=True)
    cert_dna_id = db.Column(db.Integer, db.ForeignKey('certificates_dna.id'), nullable=True)

    created_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr__(self):
        return '<Event: {}>'.format(self.event)

    def __init__(self, event, admin_id, user_id, farmer_id, buyer_id, slaughterhouse_id, head_id, cert_cons_id,
                 cert_dna_id):
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

    def to_dict(self):
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
            'created_at': datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
        }
