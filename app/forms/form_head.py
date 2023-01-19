from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError, Optional

from ..models.heads import Head
from ..models.farmers import Farmer
from ..models.buyers import Buyer
from ..models.slaughterhouses import Slaughterhouse

# Importazioni necessarie per mantenere le relazioni valide
from ..models.certificates_cons import CertificateCons  # noqa
from ..models.certificates_dna import CertificateDna  # noqa


def list_head():
    records = Head.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["headset"] for d in _list if "headset" in d]
    return _list


def list_farmer():
    records = Farmer.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["farmer_name"] for d in _list if "farmer_name" in d]
    _list.append("-")
    return _list


def list_buyer():
    records = Buyer.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["buyer_name"] for d in _list if "buyer_name" in d]
    _list.append("-")
    return _list


def list_slaughterhouse():
    records = Slaughterhouse.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["slaughterhouse"] for d in _list if "slaughterhouse" in d]
    _list.append("-")
    return _list


class FormHeadCreate(FlaskForm):
    """Form inserimento dati Capo."""
    headset = StringField('Auricolare', validators=[DataRequired("Campo obbligatorio!"), Length(min=14, max=14)])

    birth_date = DateField('Data Nascita', format='%Y-%m-%d', default=datetime.now())

    castration_date = DateField('Castrazione', format='%Y-%m-%d', default="", validators=[Optional()])
    slaughter_date = DateField('Macellazione', format='%Y-%m-%d', default="", validators=[Optional()])
    sale_date = DateField('Vendita', format='%Y-%m-%d', default="", validators=[Optional()])

    farmer_id = SelectField("Allevatore", choices=list_farmer(), default="")
    buyer_id = SelectField("Acquirente", choices=list_buyer(), default="", validators=[Optional()])
    slaughterhouse_id = SelectField("Macello", choices=list_slaughterhouse(), default="", validators=[Optional()])

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")

    @staticmethod
    def validate_headset(field):
        """Valida campo headset."""
        if field.data not in ["", "-", None] and field.data.strip() in list_head():
            raise ValidationError("E' già presente un CAPO con lo stesso AURICOLARE.")

    @staticmethod
    def validate_farmer_id(field):
        """Valida campo farmer_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_farmer():
            raise ValidationError("Nessun ALLEVATORE presente con con la Ragione Sociale inserita.")

    @staticmethod
    def validate_buyer_id(field):
        """Valida campo buyer_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_buyer():
            raise ValidationError("Nessun ACQUIRENTE presente con con la Ragione Sociale inserita.")

    @staticmethod
    def validate_slaughterhouse_id(field):
        """Valida campo slaughterhouse_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_slaughterhouse():
            raise ValidationError("Nessun MACELLO presente con con la Ragione Sociale inserita.")


class FormHeadUpdate(FlaskForm):
    """Form modifica dati Capo."""
    id = IntegerField('ID')
    headset = StringField('Auricolare', validators=[DataRequired("Campo obbligatorio!"), Length(min=14, max=14)])

    birth_date = DateField('Data Nascita', format='%Y-%m-%d', default=datetime.now())
    castration_date = DateField('Castrazione', format='%Y-%m-%d', default="", validators=[Optional()])
    slaughter_date = DateField('Macellazione', format='%Y-%m-%d', default="", validators=[Optional()])
    sale_date = DateField('Vendita', format='%Y-%m-%d', default="", validators=[Optional()])

    farmer_id = SelectField("Allevatore", choices=list_farmer(), default="-")
    buyer_id = SelectField("Acquirente", choices=list_buyer(), default="-", validators=[Optional()])
    slaughterhouse_id = SelectField("Macello", choices=list_slaughterhouse(), default="-", validators=[Optional()])

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("SAVE")

    @staticmethod
    def validate_farmer_id(self, field):  # noqa
        """Valida campo farmer_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_farmer():
            raise ValidationError("Nessun ALLEVATORE presente con con la Ragione Sociale inserita.")

    @staticmethod
    def validate_buyer_id(self, field):  # noqa
        """Valida campo buyer_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_buyer():
            raise ValidationError("Nessun ACQUIRENTE presente con con la Ragione Sociale inserita.")

    @staticmethod
    def validate_slaughterhouse_id(self, field):  # noqa
        """Valida campo slaughterhouse_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_slaughterhouse():
            raise ValidationError("Nessun MACELLO presente con con la Ragione Sociale inserita.")
