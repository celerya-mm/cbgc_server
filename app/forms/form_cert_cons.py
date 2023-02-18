from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from ..app import db
from ..models.certificates_cons import CertificateCons, year_cert_calc, year_cert_calc_update, mount_code


def list_cert():
	records = CertificateCons.query.all()
	_list = [x.to_dict() for x in records]
	_list = [d["certificate_nr"] for d in _list]
	db.session.close()
	return _list


def list_farmer():
	from ..models.farmers import Farmer

	_list = ["-"]
	try:
		records = Farmer.query.all()
		_dicts = [x.to_dict() for x in records]
		db.session.close()
		for d in _dicts:
			_list.append(f"{str(d['id'])} - {d['farmer_name']}")
	except Exception as err:
		db.session.close()
		print(err)
		pass
	return _list


def list_slaughterhouses():
	from ..models.slaughterhouses import Slaughterhouse

	_list = ["-"]
	try:
		records = Slaughterhouse.query.all()
		_dicts = [x.to_dict() for x in records]
		db.session.close()
		for d in _dicts:
			_list.append(f"{str(d['id'])} - {d['slaughterhouse']}")
	except Exception as err:
		db.session.close()
		print(err)
		pass
	return _list


def list_buyers():
	from ..models.buyers import Buyer

	_list = ["-"]
	try:
		records = Buyer.query.all()
		_dicts = [x.to_dict() for x in records]
		db.session.close()
		for d in _dicts:
			_list.append(f"{str(d['id'])} - {d['buyer_name']}")
	except Exception as err:
		db.session.close()
		print(err)
		pass
	return _list


def list_heads():
	from ..models.heads import Head

	_list = ["-"]
	try:
		records = Head.query.all()
		_dicts = [x.to_dict() for x in records]
		db.session.close()
		for d in _dicts:
			_list.append(f"{str(d['id'])} - {d['headset']}")
	except Exception as err:
		db.session.close()
		print(err)
		pass
	return _list


def calc_id():  # noqa
	"""Calcola l'id per il nuovo certificato."""
	try:
		certificates = CertificateCons.query.all()
		old = max(certificates, key=lambda x: x.id)
		today = datetime.now()
		if today.month >= 7 > old.certificate_date.month and today.year == old.certificate_date.year:
			new_id = 1
		elif old.certificate_date.month < 7 and today.year > old.certificate_date.year:
			new_id = 1
		else:
			new_id = old.certificate_id + 1
		db.session.close()
		return new_id
	except Exception as err:
		db.session.close()
		print(err)
		return None


class FormCertConsCreate(FlaskForm):
	"""Form inserimento dati Certificato Consorzio."""
	certificate_id = IntegerField('ID', validators=[DataRequired("Campo obbligatorio!")], default=calc_id())

	certificate_var = StringField('Nota ID', validators=[Length(max=10), Optional()])
	certificate_date = DateField(
		'Data', validators=[DataRequired("Campo obbligatorio!")], format='%Y-%m-%d', default=datetime.now()
	)
	certificate_year = IntegerField('Anno', validators=[DataRequired("Campo obbligatorio!")],
									default=year_cert_calc())

	emitted = SelectField("Emesso", choices=["SI", "NO"], default="NO")

	cockade_id = IntegerField('ID Cocc.', validators=[Optional()], default=calc_id())
	cockade_var = StringField('Nota ID', validators=[Length(max=10), Optional()])

	sale_type = SelectField(
		"Tipo Vendita", validators=[DataRequired("Campo obbligatorio!")],
		choices=["Capo intero", "Mezzena", "Parti Anatomiche", "Altro", ""], default="Mezzena"
	)
	sale_quantity = FloatField("Quantità (kg)", validators=[Optional()])

	head_category = SelectField(
		'Categoria', choices=["Bue", "Manzo"], validators=[Length(max=10), Optional()], default="Bue"
	)
	head_age = IntegerField('Età', validators=[Optional()])
	batch_number = StringField('Lotto NR', validators=[Length(max=20), Optional()])

	invoice_nr = StringField('Fattura NR', validators=[Length(max=20), Optional()])
	invoice_date = DateField('Fattura Data', format='%Y-%m-%d', validators=[Optional()])
	invoice_status = SelectField(
		'Fattura Stato', validators=[DataRequired("Campo obbligatorio!")], choices=[
			"Annullata", "Da Emettere", "Emessa", "Fiera", "Non Pagata", "Pagata"
		], default="Da Emettere"
	)

	farmer_id = SelectField("Seleziona Allevatore", choices=list_farmer())
	slaughterhouse_id = SelectField("Seleziona Macello", choices=list_slaughterhouses(), default="-")
	buyer_id = SelectField("Seleziona Acquirente", choices=list_buyers(), default="-")

	head_id = SelectField("Seleziona Capo", choices=list_heads())

	note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
	note = StringField('Note', validators=[Length(max=255)])

	submit = SubmitField("CREATE")

	def __repr__(self):
		return f'<CERT_CONSORZIO CREATED - NR: {self.certificate_id.data} del {self.certificate_date.data}>'

	def __str__(self):
		return f'<CERT_CONSORZIO CREATED - NR: {self.certificate_id.data} del {self.certificate_date.data}>'

	def validate_certificate_id(self, field):  # noqa
		"""Valida campo certificato_id."""
		from ..utilitys.functions import year_extract

		if self.certificate_var.data:
			cert_nr = f'{field.data}{self.certificate_var.data}/{year_extract(self.certificate_date.data)}'
		else:
			cert_nr = f'{field.data}/{year_extract(self.certificate_date.data)}'

		if field.data not in ["", "-", None] and cert_nr.strip() in list_cert():
			raise ValidationError(f"E' già presente un certificato con lo stesso identificativo {cert_nr}.")

	def validate_invoice_status(self, field):  # noqa
		"""Valida campo invoice_status."""
		if self.invoice_date.data and field.data == "Da Emettere":
			raise ValidationError(f"Attenzione, la fattura non può avere una data di emissione e lo stato essere da"
								  f"'Da Emettere'.")
		if self.invoice_nr.data and field.data == "Da Emettere":
			raise ValidationError(f"Attenzione, la fattura non può essere presente e lo stato essere da 'Da Emettere'.")

	def validate_head_category(self, field):  # noqa
		"""Valida campo categoria capo."""
		if self.head_age.data >= 46 and field.data == "Manzo":
			raise ValidationError(f"Attenzione, il capo ha 46 o più mesi. Devi assegnare la categoria 'Bue'.")
		if self.head_age.data < 46 and field.data == "Bue":
			raise ValidationError(f"Attenzione, il capo ha meno di 46 mesi. Devi assegnare la categoria 'Manzo'.")

	def to_dict(self):
		"""Converte form in dict."""
		from ..utilitys.functions import date_to_str, status_si_no
		return {
			'certificate_id': self.certificate_id.data,
			'certificate_var': self.certificate_var.data,

			'certificate_date': date_to_str(self.certificate_date.data),
			'emitted': status_si_no(self.emitted.data),

			'cockade_id': self.cockade_id.data,
			'cockade_var': self.cockade_var.data,

			'head_category': self.head_category.data,
			'head_age': self.head_age.data,
			'batch_number': self.batch_number.data,

			'sale_type': self.sale_type.data,
			'sale_quantity': self.sale_quantity.data,
			'sale_rest': self.sale_quantity.data,

			'invoice_nr': self.invoice_nr.data,
			'invoice_date': date_to_str(self.invoice_date.data),
			'invoice_status': self.invoice_status.data,

			'head_id': self.head_id.data,
			'buyer_id': self.buyer_id.data,
			'farmer_id': self.farmer_id.data,
			'slaughterhouse_id': self.slaughterhouse_id,

			'note_certificate': self.note_certificate.data,
			'note': self.note.data,
		}


class FormCertConsUpdate(FlaskForm):
	"""Form inserimento dati Certificato Consorzio."""
	certificate_id = IntegerField('ID', validators=[DataRequired("Campo obbligatorio!")])

	certificate_var = StringField('Nota ID', validators=[Length(max=10), Optional()])
	certificate_date = DateField(
		'Data', validators=[DataRequired("Campo obbligatorio!")], format='%Y-%m-%d'
	)
	certificate_year = IntegerField('Anno', validators=[DataRequired("Campo obbligatorio!")])

	emitted = SelectField("Emesso", choices=["SI", "NO"])

	cockade_id = IntegerField('ID Cocc.', validators=[Optional()])
	cockade_var = StringField('Nota ID', validators=[Length(max=10), Optional()])

	sale_type = SelectField(
		"Tipo", validators=[DataRequired("Campo obbligatorio!")],
		choices=["Capo intero", "Mezzena", "Parti Anatomiche", "Altro", ""]
	)
	sale_quantity = FloatField("kg", validators=[Optional()])
	sale_rest = FloatField("Rimanenti", validators=[Optional()])

	head_category = SelectField('Categoria', choices=["Bue", "Manzo"], validators=[Length(max=10), Optional()])
	head_age = IntegerField('Età', validators=[Optional()])
	batch_number = StringField('Lotto NR', validators=[Length(max=20), Optional()])

	invoice_nr = StringField('Fattura Nr.', validators=[Length(max=20), Optional()])
	invoice_date = DateField('Fattura Data', format='%Y-%m-%d', validators=[Optional()])
	invoice_status = SelectField(
		'Fattura Stato', validators=[DataRequired("Campo obbligatorio!")], choices=[
			"Annullata", "Da Emettere", "Emessa", "Fiera", "Non Pagata", "Pagata"
		]
	)

	head_id = SelectField("Sel. Capo", choices=list_heads())
	farmer_id = SelectField("Sel. Allevatore", choices=list_farmer())
	buyer_id = SelectField("Sel. Acquirente", choices=list_buyers())
	slaughterhouse_id = SelectField("Sel. Macello", choices=list_slaughterhouses())

	note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
	note = StringField('Note', validators=[Length(max=255)])

	submit = SubmitField("Update")

	def __repr__(self):
		return f'<CERT_CONSORZIO UPDATED - NR: {self.certificate_id.data} del {self.certificate_date.data}>'

	def __str__(self):
		return f'<CERT_CONSORZIO UPDATED - NR: {self.certificate_id.data} del {self.certificate_date.data}>'

	def validate_invoice_status(self, field):  # noqa
		"""Valida campo invoice_status."""
		if self.invoice_date.data and field.data == "Da Emettere":
			raise ValidationError(f"Attenzione, la fattura non può avere una data di emissione e lo stato essere da"
								  f"'Da Emettere'.")
		if self.invoice_nr.data and field.data == "Da Emettere":
			raise ValidationError(f"Attenzione, la fattura non può essere presente e lo stato essere da 'Da Emettere'.")

	def validate_head_category(self, field):  # noqa
		"""Valida campo categoria capo."""
		if self.head_age.data >= 46 and field.data == "Manzo":
			raise ValidationError(f"Attenzione, il capo ha 46 o più mesi. Devi assegnare la categoria 'Bue'.")
		if self.head_age.data < 46 and field.data == "Bue":
			raise ValidationError(f"Attenzione, il capo ha meno di 46 mesi. Devi assegnare la categoria 'Manzo'.")

	def to_dict(self):
		"""Converte form in dict."""
		from ..utilitys.functions import date_to_str, status_true_false, not_empty

		certificate_year = year_cert_calc_update(self.certificate_date.data)

		return {
			'certificate_id': self.certificate_id.data,
			'certificate_var': self.certificate_var.data,

			'certificate_date': date_to_str(self.certificate_date.data, "%Y-%m-%d"),
			'certificate_year': certificate_year,
			'certificate_nr': mount_code(self.certificate_id.data, certificate_year, self.certificate_var.data),

			'emitted': status_true_false(self.emitted.data),

			'cockade_id': not_empty(self.cockade_id.data),
			'cockade_var': self.cockade_var.data,
			'cockade_nr': mount_code(self.cockade_id.data, certificate_year, self.cockade_var.data),

			'sale_type': not_empty(self.sale_type.data),
			'sale_quantity': self.sale_quantity.data,
			'sale_rest': self.sale_rest.data,

			'head_age': not_empty(self.head_age.data),
			'head_category': not_empty(self.head_category.data),
			'batch_number': not_empty(self.batch_number.data),

			'invoice_nr': not_empty(self.invoice_nr.data),
			'invoice_date': date_to_str(self.invoice_date.data, "%Y-%m-%d"),
			'invoice_status': not_empty(self.invoice_status.data),

			'head_id': self.head_id.data.split(' - ')[0] if self.head_id.data not in ['', '-', None] else None,
			'buyer_id': self.buyer_id.data.split(' - ')[0] if self.buyer_id.data not in ['', '-', None] else None,
			'farmer_id': self.farmer_id.data.split(' - ')[0] if self.farmer_id.data not in ['', '-', None] else None,
			'slaughterhouse_id': self.slaughterhouse_id.data.split(' - ')[0] if self.slaughterhouse_id.data not in ['', '-', None] else None,

			'note_certificate': not_empty(self.note_certificate.data),
			'note': not_empty(self.note.data),
			'updated_at': datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
		}


class FormCertConsUpdateBuyer(FlaskForm):
	"""Form inserimento dati Certificato Consorzio."""
	certificate_nr = IntegerField('Certificato nr.')
	sale_rest = FloatField("kg Rimanenti", validators=[DataRequired("Campo obbligatorio!")])
	prev = FloatField("kg Rimanenti", validators=[Optional()])

	submit = SubmitField("Update")

	def validate_sale_rest(self, field):  # noqa
		"""Valida campo sale_rest."""
		if field.data > self.prev.data:
			raise ValidationError(f"Attenzione, non puoi assegnare un quantitativo superiore a quello assegnato o "
								  f"precedentemente modificato.")

	def __repr__(self):
		return f'<CERT_CONSORZIO UPDATED - NR: {self.certificate_nr.data}>'

	def __str__(self):
		return f'<CERT_CONSORZIO UPDATED - NR: {self.certificate_nr.data}>'

	def to_dict(self):
		"""Converte form in dict."""
		return {
			'certificate_nr': self.certificate_nr.data,
			'sale_rest': self.sale_rest.data,
		}
