from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Length, ValidationError, Optional

from ..models.buyers import Buyer
from ..models.certificates_cons import CertificateCons  # noqa
from ..models.certificates_dna import CertificateDna  # noqa
from ..models.farmers import Farmer
from ..models.heads import Head, verify_castration
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

    def __repr__(self):
        return f'<HEAD CREATED - headset: {self.headset.data}>'

    def __str__(self):
        return f'<HEAD CREATED - headset: {self.headset.data}>'

    def validate_headset(Self, field):  # noqa
        """Valida campo headset."""
        if field.data not in ["", "-", None] and field.data.strip() in list_head():
            raise ValidationError("E' già presente un CAPO con lo stesso AURICOLARE.")

    def validate_farmer_id(Self, field):  # noqa
        """Valida campo farmer_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_farmer():
            raise ValidationError("Nessun ALLEVATORE presente corrispondente alla Ragione Sociale inserita.")

    def validate_buyer_id(Self, field):  # noqa
        """Valida campo buyer_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_buyer():
            raise ValidationError("Nessun ACQUIRENTE presente corrispondente alla Ragione Sociale inserita.")

    def validate_slaughterhouse_id(Self, field):  # noqa
        """Valida campo slaughterhouse_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_slaughterhouse():
            raise ValidationError("Nessun MACELLO presente corrispondente alla Ragione Sociale inserita.")


class FormHeadUpdate(FlaskForm):
    """Form modifica dati Capo."""
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

    def __repr__(self):
        return f'<HEAD UPDATED - headset: {self.headset.data}>'

    def __str__(self):
        return f'<HEAD UPDATED - headset: {self.headset.data}>'

    def validate_farmer_id(self, field):  # noqa
        """Valida campo farmer_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_farmer():
            raise ValidationError("Nessun ALLEVATORE presente corrispondente alla Ragione Sociale inserita.")

    def validate_buyer_id(self, field):  # noqa
        """Valida campo buyer_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_buyer():
            raise ValidationError("Nessun ACQUIRENTE presente corrispondente alla Ragione Sociale inserita.")

    def validate_slaughterhouse_id(self, field):  # noqa
        """Valida campo slaughterhouse_id."""
        if field.data not in ["", "-", None] and field.data.strip() not in list_slaughterhouse():
            raise ValidationError("Nessun MACELLO presente corrispondente alla Ragione Sociale inserita.")

    def to_dict(self, dna_cer=None, cons_cert=None):
        """Converte form in dict."""
        from ..utilitys.functions import date_to_str, year_extract
        return {
            'headset': self.headset.data,

            'birth_date': date_to_str(self.birth_date.data),
            'birth_year': year_extract(self.birth_date.data),

            'castration_date': date_to_str(self.castration_date.data),
            'castration_year': year_extract(self.castration_date.data),
            'castration_compliance': verify_castration(self.birth_date.data, self.castration_date.data),

            'slaughter_date': date_to_str(self.slaughter_date.data),

            'sale_date': date_to_str(self.sale_date.data),
            'sale_year': year_extract(self.sale_date.data),

            'farmer_id': self.farmer_id.data,
            'buyer_id': self.buyer_id.data,
            'slaughterhouse_id': self.slaughterhouse_id.data,

            'dna_cert': dna_cer,
            'cons_cert': cons_cert,

            'note_certificate': self.note_certificate.data,
            'note': self.note.data,
        }

    def to_db(self, dna_cer=None, cons_cert=None):
        """Converte form in dict."""
        from ..utilitys.functions import str_to_date, year_extract
        return {
            'headset': self.headset.data,

            'birth_date': str_to_date(self.birth_date.data),
            'birth_year': year_extract(self.birth_date.data),

            'castration_date': str_to_date(self.castration_date.data),
            'castration_year': year_extract(self.castration_date.data),
            'castration_compliance': verify_castration(self.birth_date.data, self.castration_date.data),

            'slaughter_date': str_to_date(self.slaughter_date.data),

            'sale_date': str_to_date(self.sale_date.data),
            'sale_year': year_extract(self.sale_date.data),

            'farmer_id': self.farmer_id.data,
            'buyer_id': self.buyer_id.data,
            'slaughterhouse_id': self.slaughterhouse_id.data,

            'dna_cert': dna_cer,
            'cons_cert': cons_cert,

            'note_certificate': self.note_certificate.data,
            'note': self.note.data,
        }
