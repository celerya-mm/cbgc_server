from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional

from ..models.accounts import User
from ..models.buyers import Buyer
from ..models.certificates_cons import CertificateCons  # noqa
from ..models.heads import Head  # noqa


def list_buyer():
    records = Buyer.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["buyer_name"] for d in _list if "buyer_name" in d]
    return _list


def list_user():
    records = User.query.all()
    _dicts = [x.to_dict() for x in records]
    _list = ["-"]
    for d in _dicts:
        _list.append(f"{str(d['id'])} - {d['username']}")
    return _list


class FormBuyerCreate(FlaskForm):
    """Form inserimento dati Acquirente."""
    buyer_name = StringField(
        'Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=100)]
    )

    buyer_type = SelectField("Tipo Acquirente", choices=["Macelleria", "Macello", "Ristorante"], default="Ristorante")

    email = EmailField('Email', validators=[Email(), Length(max=80), Optional()])
    phone = StringField('Telefono', validators=[Length(min=7, max=80), Optional()], default="+39 ")

    address = StringField('Indirizzo', validators=[Length(min=5, max=255), Optional()])
    cap = StringField('CAP', validators=[Length(min=5, max=5), Optional()])
    city = StringField('Città', validators=[Length(min=3, max=55), Optional()])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())
    affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"], default="SI")

    user_id = SelectField("Assegna Utente", choices=list_user(), default="-", validators=[Optional()])

    note_certificate = StringField('Note Certificato', validators=[Length(max=255), Optional()])
    note = StringField('Note', validators=[Length(max=255), Optional()])

    submit = SubmitField("CREATE")

    def __repr__(self):
        return f'<BUYER CREATED - Rag. Sociale: {self.buyer_name.data}>'

    def __str__(self):
        return f'<BUYER CREATED - Rag. Sociale: {self.buyer_name.data}>'

    def validate_buyer_name(self, field):  # noqa
        """Valida Ragione Sociale."""
        if field.data.strip() in list_buyer():
            raise ValidationError("E' già presente un ACQUIRENTE con la stessa Ragione Sociale.")

    def validate_user_id(self, field):  # noqa
        """Valida campo farmer_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_user():
            raise ValidationError("Nessun UTENTE presente corrispondente all'USERNAME inserito.")


class FormBuyerUpdate(FlaskForm):
    """Form modifica dati Acquirente."""
    buyer_name = StringField(
        'Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=100)]
    )
    buyer_type = SelectField("Tipo Acquirente", choices=["Macelleria", "Macello", "Ristorante"])

    email = EmailField('Email', validators=[Email(), Length(max=80), Optional()])
    phone = StringField('Telefono', validators=[Length(min=7, max=80), Optional()])

    address = StringField('Indirizzo', validators=[Length(min=5, max=255), Optional()])
    cap = StringField('CAP', validators=[Length(min=5, max=5), Optional()])
    city = StringField('Città', validators=[Length(min=3, max=55), Optional()])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', validators=[Optional()])
    affiliation_end_date = DateField('Data affiliazione', format='%Y-%m-%d', validators=[Optional()])
    affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"])

    user_id = SelectField("Utente Assegnato", choices=list_user(), validators=[Optional()])

    note_certificate = StringField('Note Certificato', validators=[Length(max=255), Optional()])
    note = StringField('Note', validators=[Length(max=255), Optional()])

    submit = SubmitField("SAVE")

    def __repr__(self):
        return f'<BUYER UPDATED - Rag. Sociale: {self.buyer_name.data}>'

    def __str__(self):
        return f'<BUYER UPDATED - Rag. Sociale: {self.buyer_name.data}>'

    def validate_affiliation_status(self, field):
        """Valida stato affiliazione in base alle date inserite."""
        if field.data == "NO" and self.affiliation_end_date.data not in [None, ""]:
            raise ValidationError("Attenzione lo Stato Affiliazione non può essere SI se è presente una data di "
                                  "cessazione affiliazione.")

    def validate_user_id(self, field):  # noqa
        """Valida campo farmer_id."""
        if field.data not in ["", None] and field.data.strip() not in list_user():
            raise ValidationError("Nessun UTENTE presente corrispondente all'USERNAME inserito.")

    def to_dict(self):
        """Converte form in dict."""
        from ..utilitys.functions import date_to_str, address_mount, status_si_no
        return {
            'buyer_name': self.buyer_name.data,
            'buyer_type': self.buyer_type.data,

            'email': self.email.data,
            'phone': self.phone.data,

            'address': self.address.data,
            'cap': self.cap.data,
            'city': self.city.data,
            'full_address': address_mount(self.address.data, self.cap.data, self.city.data),

            'affiliation_start_date': date_to_str(self.affiliation_start_date.data),
            'affiliation_end_date': date_to_str(self.affiliation_end_date.data),
            'affiliation_status': status_si_no(self.affiliation_status.data),

            'note_certificate': self.note_certificate.data,
            'note': self.note.data,
        }
