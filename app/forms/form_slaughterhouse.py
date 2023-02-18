from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional

from ..models.certificates_cons import CertificateCons  # noqa
from ..models.heads import Head  # noqa
from ..models.slaughterhouses import Slaughterhouse


def list_slaughterhouse():
	records = Slaughterhouse.query.all()
	_list = [x.to_dict() for x in records]
	_list = [d["slaughterhouse"] for d in _list if "slaughterhouse" in d]
	return _list


def list_slaughterhouse_code():
	records = Slaughterhouse.query.all()
	_list = [x.to_dict() for x in records]
	_list = [d["slaughterhouse_code"] for d in _list if "slaughterhouse_code" in d]
	return _list


class FormSlaughterhouseCreate(FlaskForm):
	"""Form inserimento dati Macello."""
	slaughterhouse = StringField(
		'Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=100)]
	)

	slaughterhouse_code = StringField('Codice Macello', validators=[Length(max=20), Optional()])

	email = EmailField('Email', validators=[Email(), Length(max=80), Optional()])
	phone = StringField('Telefono', validators=[Length(min=7, max=80), Optional()], default="+39 ")

	address = StringField('Indirizzo', validators=[Length(min=5, max=255), Optional()])
	cap = StringField('CAP', validators=[Length(min=5, max=5), Optional()])
	city = StringField('Città', validators=[Length(min=3, max=55), Optional()])
	coordinates = StringField('Coordinate', validators=[Length(max=100), Optional()])

	affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', validators=[Optional()], default="")
	affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"], default="NO")

	note = StringField('Note', validators=[Length(max=255), Optional()])

	submit = SubmitField("CREATE")

	def __repr__(self):
		return f'<SLAUGHTERHOUSE CREATED - Rag. Sociale: {self.slaughterhouse.data}>'

	def __str__(self):
		return f'<SLAUGHTERHOUSE CREATED - Rag. Sociale: {self.slaughterhouse.data}>'

	def validate_slaughterhouse(self, field):  # noqa
		if self.slaughterhouse.data.strip() in list_slaughterhouse():
			raise ValidationError("E' già presente un MACELLO con la stessa Ragione Sociale.")

	def validate_slaughterhouse_code(self, field):  # noqa
		if self.slaughterhouse_code.data.strip() in list_slaughterhouse_code():
			raise ValidationError("E' già presente un MACELLO con lo stesso codice.")


class FormSlaughterhouseUpdate(FlaskForm):
	"""Form modifica dati Macello."""
	slaughterhouse = StringField(
		'Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=100)]
	)

	slaughterhouse_code = StringField('Codice Macello', validators=[Length(max=20), Optional()])

	email = EmailField('Email', validators=[Email(), Length(max=80), Optional()])
	phone = StringField('Telefono', validators=[Length(min=7, max=80), Optional()])

	address = StringField('Indirizzo', validators=[Length(min=5, max=255), Optional()])
	cap = StringField('CAP', validators=[Length(min=5, max=5), Optional()])
	city = StringField('Città', validators=[Length(min=3, max=55), Optional()])
	coordinates = StringField('Coordinate', validators=[Length(max=100), Optional()])

	affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', validators=[Optional()])
	affiliation_end_date = DateField('Cessazione', format='%Y-%m-%d', validators=[Optional()])
	affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"])

	note = StringField('Note', validators=[Length(max=255)])

	submit = SubmitField("CREATE")

	def __repr__(self):
		return f'<SLAUGHTERHOUSE UPDATED - Rag. Sociale: {self.slaughterhouse.data}>'

	def __str__(self):
		return f'<SLAUGHTERHOUSE UPDATED - Rag. Sociale: {self.slaughterhouse.data}>'

	def to_dict(self):
		"""Converte form in dict."""
		from ..utilitys.functions import date_to_str, status_true_false, address_mount, not_empty
		return {
			'slaughterhouse': self.slaughterhouse.data.strip(),
			'slaughterhouse_code': self.slaughterhouse_code.data.strip(),

			'email': not_empty(self.email.data),
			'phone': not_empty(self.phone.data),

			'address': not_empty(self.address.data),
			'cap': not_empty(self.cap.data),
			'city': not_empty(self.city.data),
			'full_address': address_mount(self.address.data, self.cap.data, self.city.data),
			'coordinates': not_empty(self.coordinates.data),

			'affiliation_start_date': date_to_str(self.affiliation_start_date.data),
			'affiliation_end_date': date_to_str(self.affiliation_end_date.data),
			'affiliation_status': status_true_false(self.affiliation_status.data),

			'note': not_empty(self.note.data),
			'updated_at': date_to_str(datetime.now(), "%Y-%m-%d %H:%M:%S")
		}
