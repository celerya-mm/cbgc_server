from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, ValidationError


def pdf_to_byte(_pdf):
    """Converte file in byte."""
    return _pdf


class FormCertDnaCreate(FlaskForm):
    """Form inserimento dati Certificato DNA."""
    dna_cert_id = StringField('ID', validators=[DataRequired("Campo obbligatorio!"), Length(max=20)])
    dna_cert_date = DateField(
        'Data Certificato', format='%Y-%m-%d',
        validators=[DataRequired("Campo obbligatorio!")]
    )

    note = StringField('Note Record', validators=[Length(max=255), Optional()])

    submit = SubmitField("CREATE")

    def __repr__(self):
        return f'<CERT_DNA - Nr: {self.dna_cert_id.data} del {self.dna_cert_date.data}>'

    def __str__(self):
        return f'<CERT_DNA - Nr: {self.dna_cert_id.data} del {self.dna_cert_date.data}>'

    def to_dict(self, dna_cert_id, dna_cert_date, head_id, farmer_id, note):  # noqa
        """Converte form in dict."""
        from ..utilitys.functions import date_to_str, year_extract
        return {
            'dna_cert_id': dna_cert_id,
            'dna_cert_date': date_to_str(dna_cert_date),
            'dna_cert_year': year_extract(dna_cert_date),
            'dna_cert_nr': f"{dna_cert_id}/{year_extract(dna_cert_date)}",

            'head_id:': head_id,
            'farmer_id': farmer_id,

            'note': note
        }


class FormCertDnaUpdate(FlaskForm):
    """Form inserimento dati Certificato DNA."""
    dna_cert_id = StringField('ID', validators=[DataRequired("Campo obbligatorio!"), Length(max=20)])
    dna_cert_date = DateField(
        'Data Certificato', format='%Y-%m-%d',
        validators=[DataRequired("Campo obbligatorio!")]
    )

    head_id = IntegerField("Capo", validators=[DataRequired("Campo obbligatorio!")])
    farmer_id = IntegerField("Allevatore", validators=[DataRequired("Campo obbligatorio!")])

    note = StringField('Note Record', validators=[Length(max=255), Optional()])

    submit = SubmitField("CREATE")

    def __repr__(self):
        return f'<CERT_DNA - Nr: {self.dna_cert_id.data} del {self.dna_cert_date.data}>'

    def __str__(self):
        return f'<CERT_DNA - Nr: {self.dna_cert_id.data} del {self.dna_cert_date.data}>'

    def to_dict(self, dna_cert_id, dna_cert_date, head_id, farmer_id, note):  # noqa
        """Converte form in dict."""
        from ..utilitys.functions import date_to_str, year_extract
        return {
            'dna_cert_id': dna_cert_id,
            'dna_cert_date': date_to_str(dna_cert_date),
            'dna_cert_year': year_extract(dna_cert_date),
            'dna_cert_nr': f"{dna_cert_id}/{year_extract(dna_cert_date)}",

            'head_id:': head_id,
            'farmer_id': farmer_id,

            'note': note
        }
