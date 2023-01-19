from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional

from ..models.slaughterhouses import Slaughterhouse

# Importazioni necessarie per mantenere le relazioni valide
from ..models.heads import Head  # noqa
from ..models.certificates_cons import CertificateCons  # noqa


def list_slaughterhouse():
    records = Slaughterhouse.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["slaughterhouse"] for d in _list if "slaughterhouse" in d]
    return _list


class FormSlaughterhouseCreate(FlaskForm):
    """Form inserimento dati Macello."""
    slaughterhouse = StringField(
        'Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=100)]
    )

    slaughterhouse_code = StringField('Codice Macello', validators=[Length(min=3, max=20), Optional()])

    email = EmailField('Email', validators=[Email(), Length(max=80), Optional()])
    phone = StringField('Telefono', validators=[Length(min=7, max=80), Optional()], default="+39 ")

    address = StringField('Indirizzo', validators=[Length(min=5, max=255), Optional()])
    cap = StringField('CAP', validators=[Length(min=5, max=5), Optional()])
    city = StringField('Città', validators=[Length(min=3, max=55), Optional()])

    affiliation_start_date = DateField(
        'Data affiliazione', format='%Y-%m-%d', default=datetime.now(), validators=[Optional()])
    affiliation_status = SelectField("Affiliazione", choices=["-", "SI", "NO"], default="-")

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")

    @staticmethod
    def validate_slaughterhouse(self, field):  # noqa
        if field.data.strip() in list_slaughterhouse():
            raise ValidationError("E' già presente un MACELLO con la stessa Ragione Sociale.")


class FormSlaughterhouseUpdate(FlaskForm):
    """Form modifica dati Macello."""
    slaughterhouse = StringField(
        'Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=100)]
    )

    slaughterhouse_code = StringField('Codice Macello', validators=[Length(min=3, max=20), Optional()])

    email = EmailField('Email', validators=[Email(), Length(max=80), Optional()])
    phone = StringField('Telefono', validators=[Length(min=7, max=80), Optional()], default="+39 ")

    address = StringField('Indirizzo', validators=[Length(min=5, max=255), Optional()])
    cap = StringField('CAP', validators=[Length(min=5, max=5), Optional()])
    city = StringField('Città', validators=[Length(min=3, max=55), Optional()])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', validators=[Optional()])
    affiliation_end_date = DateField('Data affiliazione', format='%Y-%m-%d', validators=[Optional()])
    affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"])

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("SAVE")

    @staticmethod
    def validate_affiliation_status(self, field):
        """Valida stato affiliazione in base alle date inserite."""
        if field.data == "NO" and self.affiliation_end_date.data not in [None, ""]:
            raise ValidationError("Attenzione lo Stato Affiliazione non può essere SI se è presente una data di "
                                  "cessazione affiliazione.")
