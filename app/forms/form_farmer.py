from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional

from app.models.farmers import Farmer

# Importazioni necessarie per mantenere le relazioni valide
from app.models.heads import Head  # noqa
from app.models.certificates_cons import CertificateCons  # noqa
# from app.models.certificates_dna import CertificateDna  # noqa


def list_farmer():
    records = Farmer.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["farmer_name"] for d in _list if "farmer_name" in d]
    return _list


class FormFarmerCreate(FlaskForm):
    """Form inserimento dati Allevatore."""
    farmer_name = StringField('Ragione Sociale', validators=[
        DataRequired("Campo obbligatorio!"),
        Length(min=3, max=100)])

    email = EmailField('Email', validators=[Email(), Length(max=80), Optional()])
    phone = StringField('Telefono', validators=[Length(min=7, max=80), Optional()])

    address = StringField('Indirizzo', validators=[Length(min=5, max=255), Optional()])
    cap = StringField('CAP', validators=[Length(min=5, max=5), Optional()])
    city = StringField('Città', validators=[Length(min=3, max=55), Optional()])

    affiliation_start_date = DateField(
        'Data affiliazione', format='%Y-%m-%d', default=datetime.now(), validators=[Optional()])
    affiliation_status = SelectField('Stato Affiliazione', choices=["SI", "NO"], default="SI")

    stable_code = StringField('Codice Stalla', validators=[Length(min=3, max=25), Optional()])
    stable_type = SelectField("Tipo Stalla", choices=["-", "Allevamento", "Stalla di sosta"], default="Allevamento")
    stable_productive_orientation = SelectField("Orientamento Produttivo", choices=[
        "-", "Da Latte", "Da Carne", "Da Latte e Da Carne"], default="Da Carne")
    stable_breeding_methods = SelectField("Modalità Allevamento", choices=[
        "-", "Estensivo", "Intensivo", "Transumante", "Brado"], default="Estensivo")

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")

    @staticmethod
    def validate_farmer_name(self, field):
        if field.data in list_farmer():
            raise ValidationError("E' già presente un ALLEVATORE con la stessa Ragione Sociale.")


class FormFarmerUpdate(FlaskForm):
    """Form modifica dati Allevatore."""
    farmer_name = StringField('Ragione Sociale', validators=[
        DataRequired("Campo obbligatorio!"),
        Length(min=3, max=100)])

    email = EmailField('Email', validators=[Email(), Length(max=80), Optional()])
    phone = StringField('Telefono', validators=[Length(min=7, max=80), Optional()])

    address = StringField('Indirizzo', validators=[Length(min=5, max=255), Optional()])
    cap = StringField('CAP', validators=[Length(min=5, max=5), Optional()])
    city = StringField('Città', validators=[Length(min=3, max=55), Optional()])

    stable_code = StringField('Codice Stalla', validators=[Length(min=3, max=25), Optional()])
    stable_type = SelectField("Tipo Stalla", choices=["-", "Allevamento", "Stalla di sosta"])
    stable_productive_orientation = SelectField("Orientamento Produttivo", choices=[
        "-", "Da Latte", "Da Carne", "Da Latte e Da Carne"])
    stable_breeding_methods = SelectField("Modalità Allevamento", choices=[
        "-", "Estensivo", "Intensivo", "Transumante", "Brado"])

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")

    def to_dict(self):
        return {
            "farmer_name": self.farmer_name.data,

            "email": self.email.data,
            "phone": self.phone,

            "address": self.address.data,
            "cap": self.cap.data,
            "city": self.city.data,

            "affiliation_start_date": self.affiliation_start_date.data,

            "stable_code": self.stable_code.data,
            "stable_type": self.stable_type.data,
            "stable_productive_orientation": self.stable_productive_orientation.data,
            "stable_breeding_methods": self.stable_breeding_methods.data,

            "note_certificate": self.note_certificate.data,
            "note": self.note.data
        }
