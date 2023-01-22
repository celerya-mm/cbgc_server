from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Length, ValidationError, Optional

from ..models.certificates_cons import CertificateCons  # noqa
from ..models.certificates_dna import CertificateDna  # noqa
from ..models.farmers import Farmer
from ..models.heads import Head, verify_castration


def list_head():
    records = Head.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["headset"] for d in _list if "headset" in d]
    return _list


def list_farmer():
    records = Farmer.query.all()
    _dicts = [x.to_dict() for x in records]
    _list = ["-"]
    for d in _dicts:
        _list.append(f"{str(d['id'])} - {d['farmer_name']}")
    return _list


class FormHeadCreate(FlaskForm):
    """Form inserimento dati Capo."""
    headset = StringField('Auricolare', validators=[DataRequired("Campo obbligatorio!"), Length(min=14, max=14)])

    birth_date = DateField('Data Nascita', format='%Y-%m-%d', default=datetime.now())

    castration_date = DateField('Castrazione', format='%Y-%m-%d', validators=[Optional()])
    slaughter_date = DateField('Macellazione', format='%Y-%m-%d', validators=[Optional()])
    sale_date = DateField('Vendita', format='%Y-%m-%d', validators=[Optional()])

    farmer_id = SelectField("Allevatore", choices=list_farmer(), default="-")

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


class FormHeadUpdate(FlaskForm):
    """Form modifica dati Capo."""
    headset = StringField('Auricolare', validators=[DataRequired("Campo obbligatorio!"), Length(min=14, max=14)])

    birth_date = DateField('Data Nascita', format='%Y-%m-%d')
    castration_date = DateField('Castrazione', format='%Y-%m-%d', validators=[Optional()])
    slaughter_date = DateField('Macellazione', format='%Y-%m-%d', validators=[Optional()])
    sale_date = DateField('Vendita', format='%Y-%m-%d', validators=[Optional()])

    farmer_id = SelectField("Allevatore", choices=list_farmer())

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

    def to_dict(self):
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

            'note_certificate': self.note_certificate.data,
            'note': self.note.data,
        }
