from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from app.models.farmers import Farmer
from app.models.heads import Head


def list_head():
	_list = [""]
	try:
		records = Head.query.all()
		_dicts = [x.to_dict() for x in records]
		for d in _dicts:
			_list.append(f"{str(d['id'])} - {d['headset']}")
	except Exception as err:
		print(err)
		pass
	return _list


def list_farmer():
	_list = [""]
	try:
		records = Farmer.query.all()
		_dicts = [x.to_dict() for x in records]
		for d in _dicts:
			_list.append(f"{str(d['id'])} - {d['farmer_name']}")
	except Exception as err:
		print(err)
		pass
	return _list


class FormCertDnaCreate(FlaskForm):
	"""Form inserimento dati Certificato DNA."""
	dna_cert_id = StringField('ID', validators=[DataRequired("Campo obbligatorio!"), Length(max=20)])
	dna_cert_date = DateField(
		'Data Certificato', format='%Y-%m-%d',
		validators=[DataRequired("Campo obbligatorio!")]
	)

	head_id = SelectField("Capo", validators=[DataRequired("Campo obbligatorio!"), Length(max=25)])
	farmer_id = SelectField("Allevatore", validators=[DataRequired("Campo obbligatorio!")])

	veterinarian = StringField('Veterinario', validators=[Length(max=50), Optional()])
	note = StringField('Note Record', validators=[Length(max=255), Optional()])

	submit = SubmitField("CREATE")

	def __repr__(self):
		return f'<CERT_DNA - Nr: {self.dna_cert_id.data} del {self.dna_cert_date.data}>'

	def __str__(self):
		return f'<CERT_DNA - Nr: {self.dna_cert_id.data} del {self.dna_cert_date.data}>'

	@classmethod
	def new(cls):
		# Instantiate the form
		form = cls()

		# Update the choices
		form.farmer_id.choices = list_farmer()
		form.head_id.choices = list_head()
		return form

	def validate_head_id(self, field):  # noqa
		"""Valida campo farmer_id."""
		if field.data not in ["", "-", None] and field.data.strip() not in list_head():
			_head = field.data.split(" - ")[1]
			raise ValidationError(f"Nessun CAPO presente corrispondente all' Auricolare inserito {_head}.")

	def validate_farmer_id(self, field):  # noqa
		"""Valida campo farmer_id."""
		if field.data not in ["", "-", None] and field.data.strip() not in list_farmer():
			raise ValidationError("Nessun ALLEVATORE presente corrispondente alla Ragione Sociale inserita.")

	def to_dict(self):
		"""Converte form in dict."""
		from ..utilitys.functions import date_to_str, year_extract
		year = year_extract(self.dna_cert_date.data)

		return {
			'dna_cert_id': self.dna_cert_id.data,
			'dna_cert_date': date_to_str(self.dna_cert_date.data),
			'dna_cert_year': year,
			'dna_cert_nr': f"{self.dna_cert_id.data}/{year}",

			'head_id:': self.head_id.data,
			'farmer_id': self.farmer_id.data,

			'veterinarian': self.veterinarian.data,

			'note': self.note.data
		}


class FormCertDnaUpdate(FlaskForm):
	"""Form inserimento dati Certificato DNA."""
	dna_cert_id = StringField('ID', validators=[DataRequired("Campo obbligatorio!"), Length(max=20)])
	dna_cert_date = DateField(
		'Data Certificato', format='%Y-%m-%d',
		validators=[DataRequired("Campo obbligatorio!")]
	)

	head_id = SelectField("Capo", validators=[DataRequired("Campo obbligatorio!"), Length(max=25)])
	farmer_id = SelectField("Allevatore", validators=[DataRequired("Campo obbligatorio!")])

	veterinarian = StringField('Veterinario', validators=[Length(max=50), Optional()])
	note = StringField('Note Record', validators=[Length(max=255), Optional()])

	submit = SubmitField("CREATE")

	def __repr__(self):
		return f'<CERT_DNA - Nr: {self.dna_cert_id.data} del {self.dna_cert_date.data}>'

	def __str__(self):
		return f'<CERT_DNA - Nr: {self.dna_cert_id.data} del {self.dna_cert_date.data}>'

	@classmethod
	def new(cls, obj):
		# Instantiate the form
		form = cls()

		form.dna_cert_id.data = obj.dna_cert_id
		form.dna_cert_date.data = obj.dna_cert_date

		# Update the choices
		form.farmer_id.choices = list_farmer()
		form.head_id.choices = list_head()

		form.veterinarian.data = obj.veterinarian
		form.note.data = obj.note
		return form

	def validate_head_id(self, field):  # noqa
		"""Valida campo farmer_id."""
		if field.data not in ["", "-", None] and field.data.strip() not in list_head():
			_head = field.data.split(" - ")[1]
			raise ValidationError(f"Nessun CAPO presente corrispondente all' Auricolare inserito {_head}.")

	def validate_farmer_id(self, field):  # noqa
		"""Valida campo farmer_id."""
		if field.data not in ["", "-", None] and field.data.strip() not in list_farmer():
			raise ValidationError("Nessun ALLEVATORE presente corrispondente alla Ragione Sociale inserita.")

	def to_dict(self):
		"""Converte form in dict."""
		from ..utilitys.functions import date_to_str, year_extract, not_empty

		year = year_extract(self.dna_cert_date.data)

		return {
			'head_id': int(self.head_id.data.split(" - ")[0]),
			'farmer_id': int(self.farmer_id.data.split(" - ")[0]),

			'dna_cert_id': self.dna_cert_id.data,
			'dna_cert_date': date_to_str(self.dna_cert_date.data),
			'dna_cert_year': year,
			'dna_cert_nr': f"{self.dna_cert_id.data}/{str(year)}",

			'veterinarian': not_empty(self.veterinarian.data),

			'note': not_empty(self.note.data.strip()),
			'updated_at': datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
		}
