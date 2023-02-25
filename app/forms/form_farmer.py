from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional

from app.models.certificates_cons import CertificateCons  # noqa
from app.models.certificates_dna import CertificateDna  # noqa
from app.models.farmers import Farmer
from app.models.heads import Head  # noqa


def list_farmer():
	try:
		records = Farmer.query.all()
		_list = [x.to_dict() for x in records]
		_list = [d["farmer_name"] for d in _list if "farmer_name" in d]
		return _list
	except Exception as err:
		print('ERROR_LIST_FARMER:', err)
		return []


class FormFarmerCreate(FlaskForm):
	"""Form inserimento dati Allevatore."""
	farmer_name = StringField('Ragione Sociale', validators=[
		DataRequired("Campo obbligatorio!"),
		Length(min=3, max=100)])

	email = EmailField('Email', validators=[Optional(), Email(), Length(max=80)])
	phone = StringField('Telefono', validators=[Optional(), Length(min=7, max=80)], default="+39 ")

	address = StringField('Indirizzo', validators=[Optional(), Length(min=5, max=150)])
	cap = StringField('CAP', validators=[Optional(), Length(min=5, max=5)])
	city = StringField('Città', validators=[Optional(), Length(min=3, max=55)])
	coordinates = StringField('Coordinate', validators=[Optional(), Length(max=100)])

	affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())
	affiliation_status = SelectField('Stato Affiliazione', choices=["SI", "NO"], default="SI")

	stable_code = StringField('Codice Stalla', validators=[Optional(), Length(min=3, max=25)])
	stable_type = SelectField("Tipo Stalla", choices=["Allevamento", "Stalla di sosta"], default="Allevamento")
	stable_productive_orientation = SelectField("Orientamento Produttivo", choices=[
		"Da Latte", "Da Carne", "Da Latte e Da Carne"], default="Da Carne")
	stable_breeding_methods = SelectField("Modalità Allevamento", choices=[
		"Estensivo", "Intensivo", "Transumante", "Brado"], default="Estensivo")

	note = TextAreaField('Note', validators=[Optional(), Length(max=255)])

	submit = SubmitField("CREATE")

	def __repr__(self):
		return f'<FARMER CREATED - Rag. Sociale: {self.farmer_name.data}>'

	def __str__(self):
		return f'<FARMER CREATED - Rag. Sociale: {self.farmer_name.data}>'

	def validate_farmer_name(self, field):  # noqa
		if field.data in list_farmer():
			raise ValidationError("E' già presente un ALLEVATORE con la stessa Ragione Sociale.")


class FormFarmerUpdate(FlaskForm):
	"""Form modifica dati Allevatore."""
	farmer_name = StringField('Ragione Sociale', validators=[
		DataRequired("Campo obbligatorio!"),
		Length(min=3, max=100)])

	email = EmailField('Email', validators=[Optional(), Email(), Length(max=80)])
	phone = StringField('Telefono', validators=[Optional(), Length(min=7, max=80)])

	address = StringField('Indirizzo', validators=[Optional(), Length(min=5, max=150)])
	cap = StringField('CAP', validators=[Optional(), Length(min=5, max=5)])
	city = StringField('Città', validators=[Optional(), Length(min=3, max=55)])
	coordinates = StringField('Coordinate', validators=[Optional(), Length(max=100)])

	stable_code = StringField('Codice Stalla', validators=[Optional(), Length(min=3, max=25)])
	stable_type = SelectField("Tipo Stalla", choices=["Allevamento", "Stalla di sosta"])
	stable_productive_orientation = SelectField("Orientamento Produttivo", choices=[
		"Da Latte", "Da Carne", "Da Latte e Da Carne"], default="Da Carne")
	stable_breeding_methods = SelectField("Modalità Allevamento", choices=[
		"Estensivo", "Intensivo", "Transumante", "Brado"])

	affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', validators=[Optional()])
	affiliation_end_date = DateField('Cessazione', format='%Y-%m-%d', validators=[Optional()])
	affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"])

	note = TextAreaField('Note', validators=[Optional(), Length(max=255)])

	submit = SubmitField("SAVE")

	def __repr__(self):
		return f'<FARMER UPDATED - Rag. Sociale: {self.farmer_name.data}>'

	def __str__(self):
		return f'<FARMER UPDATED - Rag. Sociale: {self.farmer_name.data}>'

	def validate_affiliation_status(self, field):
		"""Valida stato affiliazione in base alle date inserite."""
		if field.data == "SI" and self.affiliation_end_date.data not in [None, ""]:
			raise ValidationError(
				"Attenzione lo Stato Affiliazione non può essere SI se è presente una data di cessazione affiliazione.")

	def to_dict(self):
		"""Esporta in un dict la classe."""
		from ..utilitys.functions import date_to_str, status_true_false, address_mount, not_empty
		return {
			'farmer_name': self.farmer_name.data,

			'email': not_empty(self.email.data),
			'phone': not_empty(self.phone.data),

			'address': self.address.data.strip(),
			'cap': self.cap.data.strip(),
			'city': self.city.data.strip(),
			'full_address': address_mount(self.address.data, self.cap.data, self.city.data),
			'coordinates': not_empty(self.coordinates.data),

			'stable_code': not_empty(self.stable_code.data),
			'stable_type': not_empty(self.stable_type.data),
			'stable_productive_orientation': not_empty(self.stable_productive_orientation.data),
			'stable_breeding_methods': not_empty(self.stable_breeding_methods.data),

			'affiliation_start_date': date_to_str(self.affiliation_start_date.data),
			'affiliation_end_date': date_to_str(self.affiliation_end_date.data),
			'affiliation_status': status_true_false(self.affiliation_status.data),

			'note': not_empty(self.note.data.strip()),
			'updated_at': date_to_str(datetime.now(), "%Y-%m-%d %H:%M:%S")
		}
