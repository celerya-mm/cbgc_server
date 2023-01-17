from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models.farmers import Farmer
from app.models.heads import Head
from app.models.slaughterhouses import Slaughterhouse


def list_head():
    _heads = Head.query.all()
    _list = [x.to_dict() for x in _heads]
    _list = [d["headset"] for d in _list if "headset" in d]
    return _list


class FormHeadCreate(FlaskForm):
    """Form inserimento dati Capo."""
    headset = StringField('Auricolare', validators=[DataRequired("Campo obbligatorio!"), Length(min=14, max=14)])

    birth_date = DateField('Data Nascita', format='%Y-%m-%d', default=datetime.now())
    castration_date = DateField('Data Castrazione', format='%Y-%m-%d', default="")
    slaughter_date = DateField('Data Macellazione', format='%Y-%m-%d', default="")
    sale_date = DateField('Data Vendita', format='%Y-%m-%d', default="")

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

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")

    def validate_headset(self, field):  # noqa
        print("BUYER_NAME:", field)
        if field.data.strip() in list_head():
            raise ValidationError("E' già presente un ACQUIRENTE con la stessa Ragione Sociale.")
