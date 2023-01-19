from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from app.models.slaughterhouses import Slaughterhouse

# Importazioni necessarie per mantenere le relazioni valide
from app.models.heads import Head  # noqa
from app.models.certificates_cons import CertificateCons  # noqa


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

    slaughterhouse_code = StringField('Codice Macello', validators=[Length(min=3, max=20)])

    email = EmailField('Email', validators=[Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=80)], default="+39 ")

    address = StringField('Indirizzo', validators=[Length(min=5, max=255)])
    cap = StringField('CAP', validators=[Length(min=5, max=5)])
    city = StringField('Città', validators=[Length(min=3, max=55)])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())
    affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"], default="NO")

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

    slaughterhouse_code = StringField('Codice Macello', validators=[Length(min=3, max=20)])

    email = EmailField('Email', validators=[Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=80)], default="+39 ")

    address = StringField('Indirizzo', validators=[Length(min=5, max=255)])
    cap = StringField('CAP', validators=[Length(min=5, max=5)])
    city = StringField('Città', validators=[Length(min=3, max=55)])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")
