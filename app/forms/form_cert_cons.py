from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Optional

from ..models.buyers import Buyer
from ..models.certificates_cons import CertificateCons
from ..models.farmers import Farmer
from ..models.heads import Head
from ..models.slaughterhouses import Slaughterhouse


def calc_id():
    """Calcola l'id per il nuovo certificato."""
    certificates = CertificateCons.query.all()
    old = max(certificates, key=lambda x: x.id)
    today = datetime.now()
    if today.month >= 7 > old.certificate_date.month and today.year == old.certificate_date.year:
        new_id = 1
    elif old.certificate_date.month < 7 and today.year > old.certificate_date.year:
        new_id = 1
    else:
        new_id = old.certificate_id + 1
    return new_id


class FormCertCons(FlaskForm):
    """Form inserimento dati Certificato Consorzio."""
    certificate_id = IntegerField('ID', validators=[DataRequired("Campo obbligatorio!")], default=calc_id())

    certificate_var = StringField('Integrazione ID', validators=[Length(max=10), Optional()])
    certificate_date = DateField('Data Certificato', format='%Y-%m-%d', default=datetime.now())

    cockade_id = IntegerField('ID Coccarda', validators=[Optional()], default=certificate_id)
    cockade_var = StringField('Integrazione ID Coccarda', validators=[Length(max=10), Optional()])

    sale_type = SelectField(
        "Tipo Vendita", validators=[DataRequired("Campo obbligatorio!")],
        choices=["Capo intero", "Mezzena", "Parti Anatomiche", "Altro", ""], default=""
    )
    sale_quantity = FloatField("Quantità Venduta (kg)", validators=[Optional()])

    invoice_nr = StringField('Fattura NR', validators=[Length(max=20), Optional()])
    invoice_date = DateField('Fattura Data', format='%Y-%m-%d',validators=[Optional()], default="")
    invoice_status = SelectField(
        'Fattura Stato', validators=[DataRequired("Campo obbligatorio!")], choices=[
            "Da Emettere", "Emessa", "Annullata", "Non Pagata", "Pagata"
        ], default="Da Emettere"
    )

    farmers_list = []
    farmers = Farmer.query.all()
    for f in farmers:
        farmers_list.append(f.farmer_name)
    farmer_id = SelectField("Seleziona Allevatore", choices=farmers_list, default="")

    slaughterhouses_list = []
    slaughterhouses = Slaughterhouse.query.all()
    for s in slaughterhouses:
        slaughterhouses_list.append(s.slaughterhouse)
    slaughterhouse_id = SelectField("Seleziona Macello", choices=slaughterhouses_list, default="")

    buyer_list = []
    buyers = Buyer.query.all()
    for b in buyers:
        buyer_list.append(b.buyer_name)
    buyer_id = SelectField("Seleziona Acquirente", choices=buyer_list, default="")

    head_list = []
    heads = Head.query.all()
    for h in heads:
        head_list.append(h.headset)
    head_id = SelectField("Seleziona Capo", choices=head_list, default="")

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")

    def __repr__(self):
        return f'<CERT_CONSORZIO CREATED - NR: {self.certificate_id.data} del {self.certificate_date.data}>'

    def __str__(self):
        return f'<CERT_CONSORZIO CREATED - NR: {self.certificate_id.data} del {self.certificate_date.data}>'
