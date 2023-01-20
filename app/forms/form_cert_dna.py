from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Length

from ..models.farmers import Farmer
from ..models.heads import Head


class FormCertDNA(FlaskForm):
    """Form inserimento dati Certificato DNA."""
    dna_cert_id = StringField('ID', validators=[DataRequired("Campo obbligatorio!"), Length(max=20)])
    dna_cert_date = DateField(
        'Data Certificato', format='%Y-%m-%d', default=datetime.now(),
        validators=[DataRequired("Campo obbligatorio!"), Length(max=20)]
    )

    invoice_nr = StringField('Fattura NR', validators=[Length(max=20)])
    invoice_date = DateField('Fattura Data', format='%Y-%m-%d', default=datetime.now())
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

    head_list = []
    heads = Head.query.all()
    for h in heads:
        head_list.append(h.headset)
    head_id = SelectField("Seleziona Capo", choices=head_list, default="")

    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")

    def __repr__(self):
        return f'<CERT_DNA CREATED - Nr: {self.dna_cert_id.data} del {self.dna_cert_date.data}>'

    def __str__(self):
        return f'<CERT_DNA CREATED - Nr: {self.dna_cert_id.data} del {self.dna_cert_date.data}>'

