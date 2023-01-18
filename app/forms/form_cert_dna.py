from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Length, ValidationError, Optional

from app.models.farmers import Farmer
from app.models.heads import Head


def list_head():
    records = Head.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["headset"] for d in _list if "headset" in d]
    _list.append("-")
    return _list


def list_farmer():
    records = Farmer.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["farmer_name"] for d in _list if "farmer_name" in d]
    _list.append("-")
    return _list


class FormCertDNA(FlaskForm):
    """Form inserimento dati Certificato DNA."""
    dna_cert_id = StringField('ID', validators=[DataRequired("Campo obbligatorio!"), Length(max=20)])
    dna_cert_date = DateField(
        'Data Certificato', format='%Y-%m-%d', default=datetime.now(),
        validators=[DataRequired("Campo obbligatorio!"), Length(max=20)]
    )

    farmer_id = SelectField("Seleziona Allevatore", choices=list_farmer(), default="-")
    head_id = SelectField("Seleziona Capo", choices=list_head(), default="-")

    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")
