from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, Optional

from app.models.certificates_cons import CertificateCons  # noqa
from app.models.certificates_dna import CertificateDna  # noqa
from app.models.farmers import Farmer
from app.models.heads import Head, verify_castration


def list_head():
	try:
		records = Head.query.all()
		_list = [x.to_dict() for x in records]
		_list = [d["headset"] for d in _list if "headset" in d]
		return _list
	except Exception as err:
		print('ERROR_LIST_HEAD:', err)
		return []


def list_farmer():
	_list = ["-"]
	try:
		records = Farmer.query.all()
		_dicts = [x.to_dict() for x in records]
		for d in _dicts:
			_list.append(f"{str(d['id'])} - {d['farmer_name']}")
	except Exception as err:
		print('ERROR_LIST_FARMER', err)
		pass
	return _list


class FormHeadCreate(FlaskForm):
	"""Form inserimento dati Capo."""
	headset = StringField(
		'Auricolare', validators=[DataRequired("Campo obbligatorio!"), Length(min=13, max=15)], default="IT00499")

	birth_date = DateField('Data Nascita', format='%Y-%m-%d')

	castration_date = DateField('Castrazione', format='%Y-%m-%d', validators=[Optional()])
	slaughter_date = DateField('Macellazione', format='%Y-%m-%d', validators=[Optional()])
	sale_date = DateField('Vendita', format='%Y-%m-%d', validators=[Optional()])

	farmer_id = SelectField("Allevatore")

	note = TextAreaField('Note', validators=[Optional(), Length(max=255)])

	submit = SubmitField("CREATE")

	def __repr__(self):
		return f'<HEAD CREATED - headset: {self.headset.data}>'

	def __str__(self):
		return f'<HEAD CREATED - headset: {self.headset.data}>'

	@classmethod
	def new(cls):
		# Instantiate the form
		form = cls()

		# Update the choices
		form.farmer_id.choices = list_farmer()
		return form

	def validate_headset(self, field):  # noqa
		"""Valida campo headset."""
		if field.data not in ["", "-", None] and field.data.strip() in list_head():
			raise ValidationError("E' già presente un CAPO con lo stesso AURICOLARE.")
		if len(field.data) != 14:
			raise ValidationError(f"Il campo AURICOLARE deve avere 14 caratteri, hai inserito: {len(field.data)}")

	def validate_farmer_id(self, field):  # noqa
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

	farmer_id = SelectField("Allevatore")

	note = TextAreaField('Note', validators=[Optional(), Length(max=255)])

	submit = SubmitField("SAVE")

	def __repr__(self):
		return f'<HEAD UPDATED - headset: {self.headset.data}>'

	def __str__(self):
		return f'<HEAD UPDATED - headset: {self.headset.data}>'

	@classmethod
	def new(cls, obj):
		# Instantiate the form
		form = cls()

		form.headset.data = obj.headset

		form.birth_date.data = obj.birth_date
		form.castration_date.data = obj.castration_date
		form.slaughter_date.data = obj.slaughter_date
		form.sale_date.data = obj.sale_date

		# Update the choices
		form.farmer_id.choices = list_farmer()

		form.note.data = obj.note
		return form

	def validate_farmer_id(self, field):  # noqa
		"""Valida campo farmer_id."""
		if field.data not in ["", "-", None] and field.data.strip() not in list_farmer():
			raise ValidationError("Nessun ALLEVATORE presente corrispondente alla Ragione Sociale inserita.")

	def validate_headset(self, field):  # noqa
		"""Valida campo headset."""
		if len(field.data) != 14:
			raise ValidationError(f"Il campo AURICOLARE deve avere 14 caratteri, hai inserito: {len(field.data)}")

	def to_dict(self):
		"""Converte form in dict."""
		from ..utilitys.functions import date_to_str, year_extract, not_empty
		return {
			'headset': self.headset.data,

			'birth_date': date_to_str(self.birth_date.data),
			'birth_year': year_extract(self.birth_date.data),

			'castration_date': date_to_str(self.castration_date.data),
			'castration_compliance': verify_castration(self.birth_date.data, self.castration_date.data),

			'slaughter_date': date_to_str(self.slaughter_date.data),

			'sale_date': date_to_str(self.sale_date.data),
			'sale_year': year_extract(self.sale_date.data),

			'farmer_id': int(self.farmer_id.data.split(" - ")[0]),

			'note': not_empty(self.note.data),
			'updated_at': date_to_str(datetime.now(), "%Y-%m-%d %H:%M:%S")
		}
