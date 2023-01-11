from app.app import db


class Head(db.Model):
    # Table
    __tablename__ = 'heads'
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    headset = db.Column(db.String(), index=False, unique=True, nullable=False)
    bird_date = db.Column(db.DateTime, index=False, nullable=False)
    castration_date = db.Column(db.DateTime, index=False, nullable=True)
    castration_compliance = db.Column(db.Boolean, index=False, nullable=True)  # True if days (castration-bird) < 240
    slaughter_date = db.Column(db.DateTime, index=False, nullable=True)
    sale_date = db.Column(db.DateTime, index=False, nullable=True)
    sale_year = db.Column(db.Integer, index=False, nullable=True)
    note = db.Column(db.String(255), index=False, unique=False, nullable=True)

    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=True)
    slaughterhouse_id = db.Column(db.Integer, db.ForeignKey('slaughterhouses.id'), nullable=True)

    dna_cert = db.relationship('CertificateDna', backref='head')
    cons_cert = db.relationship('CertificateCons', backref='head')

    created_at = db.Column(db.DateTime, index=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, nullable=False)

    def __repr(self):
        return '<Head {}>'.format(self.headset)

    def __init__(self, headset, bird_date, castration_date, castration_compliance, slaughter_date, sale_date, sale_year,
                 note, farmer_id, buyer_id, dna_cert, cons_cert):
        self.headset = headset
        self.bird_date = bird_date
        self.castration_date = castration_date
        self.castration_compliance = castration_compliance
        self.slaughter_date = slaughter_date
        self.sale_date = sale_date
        self.sale_year = sale_year
        self.note = note
        self.farmer_id = farmer_id
        self.buyer_id = buyer_id
        self.dna_cert = dna_cert
        self.cons_cert = cons_cert

    def to_dict(self):
        return {
            'id': self.id,
            'headset': self.headset,
            'bird_date': self.bird_date,
            'castration_date': self.castration_date,
            'castration_compliance': self.castration_compliance,
            'slaughter_date': self.slaughter_date,
            'sale_date': self.sale_date,
            'sale_year': self.sale_year,
            'note': self.note,
            'farmer_id': self.farmer_id,
            'buyer_id': self.buyer_id,
            # 'dna_cert': self.dna_cert,
            # 'cons_cert': self.cons_cert,
        }
