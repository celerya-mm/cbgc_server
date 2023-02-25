from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional

from app.models.accounts import User
from app.models.buyers import Buyer
from app.models.certificates_cons import CertificateCons  # noqa
from app.models.heads import Head  # noqa


def list_buyer():
	try:
		records = Buyer.query.all()
		_list = [x.to_dict() for x in records]
		_list = [d["buyer_name"].lower() for d in _list if "buyer_name" in d]
		return _list
	except Exception as err:
		print('ERROR_LIST_BUYERS:', err)
		return []


def list_user():
	_list = ["-"]
	try:
		records = User.query.all()
		_dicts = [x.to_dict() for x in records]
		for d in _dicts:
			_list.append(f"{str(d['id'])} - {d['username']}")
	except Exception as err:
		print('ERROR_LIST_USER:', err)
		pass
	return _list


class FormBuyerCreate(FlaskForm):
	"""Form inserimento dati Acquirente."""
	buyer_name = StringField(
		'Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=100)]
	)

	buyer_type = SelectField("Tipo Acquirente", choices=["Macelleria", "Ristorante"], default="Ristorante")

	email = EmailField('Email', validators=[Optional(), Email(), Length(max=80)])
	phone = StringField('Telefono', validators=[Optional(), Length(min=7, max=80)], default="+39 ")

	address = StringField('Indirizzo', validators=[Optional(), Length(min=5, max=150)])
	cap = StringField('CAP', validators=[Optional(), Length(min=5, max=5)])
	city = StringField('Città', validators=[Optional(), Length(min=3, max=55)])
	coordinates = StringField('Coordinate', validators=[Optional(), Length(max=100)])

	affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())
	affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"], default="SI")

	user_id = SelectField("Assegna Utente", default="-", validators=[Optional()])

	note = TextAreaField('Note', validators=[Optional(), Length(max=255)])

	submit = SubmitField("CREATE")

	@classmethod
	def new(cls):
		# Instantiate the form
		form = cls()
		# Update the choices
		form.user_id.choices = list_user()
		return form

	def __repr__(self):
		return f'<BUYER CREATED - Rag. Sociale: {self.buyer_name.data}>'

	def __str__(self):
		return f'<BUYER CREATED - Rag. Sociale: {self.buyer_name.data}>'

	def validate_buyer_name(self, field):  # noqa
		"""Valida Ragione Sociale."""
		if field.data.strip().lower() in list_buyer():
			raise ValidationError("E' già presente un ACQUIRENTE con la stessa Ragione Sociale.")

	def validate_user_id(self, field):  # noqa
		"""Valida campo farmer_id."""
		if field.data not in ["", "-", None] and field.data.strip() not in list_user():
			raise ValidationError("Nessun UTENTE presente corrispondente all'USERNAME inserito.")


class FormBuyerUpdate(FlaskForm):
	"""Form modifica dati Acquirente."""
	buyer_name = StringField(
		'Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=100)]
	)
	buyer_type = SelectField("Tipo Acquirente", choices=["-", "Macelleria", "Ristorante"])

	email = EmailField('Email', validators=[Email(), Optional(), Length(max=80)])
	phone = StringField('Telefono', validators=[Optional(), Length(min=7, max=80)])

	address = StringField('Indirizzo', validators=[Optional(), Length(min=5, max=150)])
	cap = StringField('CAP', validators=[Optional(), Length(min=5, max=5)])
	city = StringField('Città', validators=[Optional(), Length(min=3, max=55)])
	coordinates = StringField('Coordinate', validators=[Optional(), Length(max=100)])

	affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', validators=[Optional()])
	affiliation_end_date = DateField('Cessazione', format='%Y-%m-%d', validators=[Optional()])
	affiliation_status = SelectField("Affiliazione")

	user_id = SelectField("Utente Assegnato", validators=[Optional()])

	note = TextAreaField('Note', validators=[Optional(), Length(max=255)])

	submit = SubmitField("SAVE")

	@classmethod
	def new(cls, obj):
		# Instantiate the form
		form = cls()
		form.buyer_name.data = obj.buyer_name
		form.buyer_type.data = obj.buyer_type

		form.email.data = obj.email
		form.phone.data = obj.phone

		form.address.data = obj.address
		form.cap.data = obj.cap
		form.city.data = obj.city
		form.coordinates.data = obj.coordinates

		form.affiliation_start_date.data = obj.affiliation_start_date
		form.affiliation_end_date.data = obj.affiliation_end_date
		form.affiliation_status.choices = ["SI", "NO"]

		# Update the choices
		form.user_id.choices = list_user()

		form.note.data = obj.note
		return form

	def __repr__(self):
		return f'<BUYER UPDATED - Rag. Sociale: {self.buyer_name.data}>'

	def __str__(self):
		return f'<BUYER UPDATED - Rag. Sociale: {self.buyer_name.data}>'

	def validate_affiliation_status(self, field):
		"""Valida stato affiliazione in base alle date inserite."""
		if field.data == "NO" and self.affiliation_end_date.data not in [None, ""]:
			raise ValidationError("Attenzione lo Stato Affiliazione non può essere SI se è presente una data di "
								  "cessazione affiliazione.")

	def validate_user_id(self, field):  # noqa
		"""Valida campo farmer_id."""
		if field.data not in ["", None] and field.data.strip() not in list_user():
			raise ValidationError("Nessun UTENTE presente corrispondente all'USERNAME inserito.")

	def to_dict(self):
		"""Converte form in dict."""
		from ..utilitys.functions import date_to_str, address_mount, status_true_false, not_empty
		return {
			'buyer_name': self.buyer_name.data,
			'buyer_type': self.buyer_type.data,

			'email': self.email.data,
			'phone': not_empty(self.phone.data),

			'address': self.address.data,
			'cap': self.cap.data,
			'city': self.city.data,
			'full_address': address_mount(self.address.data, self.cap.data, self.city.data),
			'coordinates': not_empty(self.coordinates.data),

			'affiliation_start_date': date_to_str(self.affiliation_start_date.data),
			'affiliation_end_date': date_to_str(self.affiliation_end_date.data),
			'affiliation_status': status_true_false(self.affiliation_status.data),

			'user_id': self.user_id.data.split(' - ')[0] if self.user_id.data not in ['', '-', None] else None,

			'note': not_empty(self.note.data),
			'updated_at': datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
		}
