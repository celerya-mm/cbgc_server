from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Optional

from ..models.buyers import Buyer
from ..models.certificates_cons import CertificateCons
from ..models.farmers import Farmer
from ..models.heads import Head
from ..models.slaughterhouses import Slaughterhouse


def list_head():
    records = Head.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["headset"] for d in _list if "headset" in d]
    return _list


def list_farmer():
    records = Farmer.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["farmer_name"] for d in _list if "farmer_name" in d]
    return _list


def list_buyer():
    records = Buyer.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["buyer_name"] for d in _list if "buyer_name" in d]
    return _list


def list_slaughterhouse():
    records = Slaughterhouse.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["slaughterhouse"] for d in _list if "slaughterhouse" in d]
    _list.append("-")
    return _list


def new_id():
    """Calcola il nuovo ID del nuovo certificato"""
    # Estraggo lista records certificati e seleziono l'ultimo
    certificates = CertificateCons.query.all()
    old = max(certificates, key=lambda x: x.id)
    # Calcolo il nuo ID.
    today = datetime.now()
    if today.month >= 7 > old.certificate_date.month and today.year == old.certificate_date.year:
        _new = 1
    elif old.certificate_date.month < 7 and today.year > old.certificate_date.year:
        _new = 1
    else:
        _new = old.certificate_id + 1
    return _new


class FormCertCons(FlaskForm):
    """Form inserimento dati Certificato Consorzio."""
    certificate_id = IntegerField('ID', validators=[DataRequired("Campo obbligatorio!")], default=new_id())

    certificate_var = StringField('Integrazione ID', validators=[Length(max=10), Optional()])
    certificate_date = DateField('Data Certificato', format='%Y-%m-%d', default=datetime.now())

    cockade_id = IntegerField('ID Coccarda', default=new_id())
    cockade_var = StringField('Integrazione ID Coccarda', validators=[Length(max=10), Optional()])

    sale_type = SelectField(
        "Tipo Vendita", validators=[DataRequired("Campo obbligatorio!")],
        choices=["Capo intero", "Mezzena", "Parti Anatomiche", "Altro (vedi note certificato)"], default=""
    )
    sale_quantity = FloatField("Quantità Venduta (kg)", validators=[Optional()])

    invoice_nr = StringField('Fattura NR', validators=[Length(max=20), Optional()])
    invoice_date = DateField('Fattura Data', format='%Y-%m-%d', default=datetime.now(), validators=[Optional()])
    invoice_status = SelectField(
        'Fattura Stato', validators=[DataRequired("Campo obbligatorio!")], choices=[
            "Da Emettere", "Emessa", "Annullata", "Non Pagata", "Pagata"
        ], default="Da Emettere")

    head_id = SelectField("Seleziona Capo", choices=list_head(), default="")
    farmer_id = SelectField("Seleziona Allevatore", choices=list_farmer(), default="")
    buyer_id = SelectField("Seleziona Acquirente", choices=list_buyer(), default="")
    slaughterhouse_id = SelectField(
        "Seleziona Macello", choices=list_slaughterhouse(), default="-", validators=[Optional()])

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")
