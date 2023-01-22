from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional

from ..models.certificates_cons import CertificateCons  # noqa
from ..models.certificates_dna import CertificateDna  # noqa
from ..models.farmers import Farmer
from ..models.heads import Head  # noqa


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
    phone = StringField('Telefono', validators=[Length(min=7, max=80), Optional()], default="+39 ")

    address = StringField('Indirizzo', validators=[Length(min=5, max=255), Optional()])
    cap = StringField('CAP', validators=[Length(min=5, max=5), Optional()])
    city = StringField('Città', validators=[Length(min=3, max=55), Optional()])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())
    affiliation_status = SelectField('Stato Affiliazione', choices=["SI", "NO"], default="SI")

    stable_code = StringField('Codice Stalla', validators=[Length(min=3, max=25)])
    stable_type = SelectField("Tipo Stalla", choices=["Allevamento", "Stalla di sosta"], default="Allevamento")
    stable_productive_orientation = SelectField("Orientamento Produttivo", choices=[
        "Da Latte", "Da Carne", "Da Latte e Da Carne"], default="Da Carne")
    stable_breeding_methods = SelectField("Modalità Allevamento", choices=[
        "Estensivo", "Intensivo", "Transumante", "Brado"], default="Estensivo")

    note_certificate = StringField('Note Certificato', validators=[Length(max=255), Optional()])
    note = StringField('Note', validators=[Length(max=255), Optional()])

    submit = SubmitField("CREATE")

    def __repr__(self):
        return f'<FARMER CREATED - Rag. Sociale: {self.farmer_name.data}>'

    def __str__(self):
        return f'<FARMER CREATED - Rag. Sociale: {self.farmer_name.data}>'

    def validate_farmer_name(self, field):  # noqa
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

    stable_code = StringField('Codice Stalla', validators=[Length(min=3, max=25)])
    stable_type = SelectField("Tipo Stalla", choices=["Allevamento", "Stalla di sosta"])
    stable_productive_orientation = SelectField("Orientamento Produttivo", choices=[
        "Da Latte", "Da Carne", "Da Latte e Da Carne"])
    stable_breeding_methods = SelectField("Modalità Allevamento", choices=[
        "Estensivo", "Intensivo", "Transumante", "Brado"])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', validators=[Optional()])
    affiliation_end_date = DateField('Cessazione', format='%Y-%m-%d', validators=[Optional()])
    affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"])

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("SAVE")

    def __repr__(self):
        return f'<FARMER UPDATED - Rag. Sociale: {self.farmer_name.data}>'

    def __str__(self):
        return f'<FARMER UPDATED - Rag. Sociale: {self.farmer_name.data}>'

    def validate_affiliation_status(self, field):
        """Valida stato affiliazione in base alle date inserite."""
        if field.data == "SI" and self.affiliation_end_date.data not in [None, ""]:
            raise ValidationError(
                "Attenzione lo Stato Affiliazione non può essere SI se è presente una data di cessazione affiliazione.")

    def to_dict(self):
        """Esporta in un dict la classe."""
        from ..utilitys.functions import date_to_str, status_si_no, address_mount
        return {
            'farmer_name': self.farmer_name.data,

            'email': self.email.data,
            'phone': self.phone.data,

            'address': self.address.data,
            'cap': self.cap.data,
            'city': self.city.data,
            'full_address': address_mount(self.address.data, self.cap.data, self.city.data),

            'stable_code': self.stable_code.data,
            'stable_type': self.stable_type.data,
            'stable_productive_orientation': self.stable_productive_orientation.data,
            'stable_breeding_methods': self.stable_breeding_methods.data,

            'affiliation_start_date': date_to_str(self.affiliation_start_date.data),
            'affiliation_end_date': date_to_str(self.affiliation_end_date),
            'affiliation_status': status_si_no(self.affiliation_status.data),

            'note_certificate': self.note_certificate.data,
            'note': self.note.data,
        }
