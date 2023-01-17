from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from app.models.accounts import User
from app.models.buyers import Buyer
from app.models.heads import Head  # noqa
from app.models.certificates_cons import CertificateCons  # noqa
from app.models.certificates_dna import CertificateDna  # noqa


def list_buyer():
    _buyers = Buyer.query.all()
    _list = [x.to_dict() for x in _buyers]
    _list = [d["buyer_name"] for d in _list if "buyer_name" in d]
    return _list


class FormBuyerCreate(FlaskForm):
    """Form inserimento dati Acquirente."""
    buyer_name = StringField(
        'Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=100)]
    )

    buyer_type = SelectField("Tipo Acquirente", choices=["Macelleria", "Macello", "Ristorante"], default="Ristorante")

    email = EmailField('Email', validators=[Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=80)], default="+39 ")

    address = StringField('Indirizzo', validators=[Length(min=5, max=255)])
    cap = StringField('CAP', validators=[Length(min=5, max=5)])
    city = StringField('Città', validators=[Length(min=3, max=55)])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())
    affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"], default="SI")

    users_list = []
    users = User.query.all()
    for user in users:
        users_list.append(f"{user.username} - {user.full_name}")

    user_id = SelectField("Utente Servizio", choices=users_list, default="")

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")

    def validate_buyer_name(self, field):  # noqa
        print("BUYER_NAME:", field)
        if field.data.strip() in list_buyer():
            raise ValidationError("E' già presente un ACQUIRENTE con la stessa Ragione Sociale.")


class FormBuyerUpdate(FlaskForm):
    """Form inserimento dati Acquirente."""
    buyer_name = StringField(
        'Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=100)]
    )
    buyer_type = SelectField("Tipo Acquirente", choices=["Macelleria", "Macello", "Ristorante"], default="Ristorante")

    email = EmailField('Email', validators=[Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=80)], default="+39 ")

    address = StringField('Indirizzo', validators=[Length(min=5, max=255)])
    cap = StringField('CAP', validators=[Length(min=5, max=5)])
    city = StringField('Città', validators=[Length(min=3, max=55)])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")
