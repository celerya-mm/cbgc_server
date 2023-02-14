from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, validators, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional

from ..models.accounts import Administrator, User
from ..utilitys.functions_accounts import psw_verify, psw_contain_usr


def list_admin():
	records = Administrator.query.all()
	_list = [x.to_dict() for x in records]
	_user = [d["username"] for d in _list if "username" in d]
	_email = [d["email"] for d in _list if "email" in d]
	return _user, _email


def list_user():
	records = User.query.all()
	_list = [x.to_dict() for x in records]
	_user = [d["username"] for d in _list if "username" in d]
	_email = [d["email"] for d in _list if "email" in d]
	return _user, _email


class FormAdminSignup(FlaskForm):
	"""Form dati signup account Administrator."""
	username = StringField(
		'Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=40)], default="")

	new_password_1 = PasswordField('Nuova Password', validators=[
		DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])
	new_password_2 = PasswordField('Conferma Password', validators=[
		DataRequired("Campo obbligatorio!"), Length(min=8, max=64),
		EqualTo('new_password_1', message='Le password non corrispondono.')
	])

	psw_changed = BooleanField('Password cambiata', default=False)

	name = StringField('Nome', validators=[Length(min=3, max=25), Optional()])
	last_name = StringField('Cognome', validators=[Length(min=3, max=25), Optional()])

	email = EmailField('email', validators=[DataRequired("Campo obbligatorio!"), Email(), Length(max=80)])
	phone = StringField('Telefono', validators=[Length(min=7, max=25), Optional()], default="+39 ")

	note = StringField('Note', validators=[Length(max=255), Optional()])

	submit = SubmitField("SIGNUP")

	def __repr__(self):
		return f'<ADMINISTRATOR SIGNUP with username: {self.username}>'

	def __str__(self):
		return f'<ADMINISTRATOR SIGNUP with username: {self.username}>'

	def validate_username(self, field):  # noqa
		"""Verifica presenza username nella tabella del DB."""
		if field.data in list_admin()[0]:
			raise ValidationError("Username già utilizzato in tabella amministratori.")
		if field.data in list_user()[0]:
			raise ValidationError("Username già utilizzato in tabella utenti.")

	def validate_email(self, field):  # noqa
		"""Verifica presenza email nella tabella del DB."""
		if field.data in list_admin()[1]:
			raise ValidationError("Email già utilizzata in tabella amministratori.")
		if field.data in list_user()[1]:
			raise ValidationError("Email già utilizzata in tabella utenti.")

	def validate_new_password_1(self, field):  # noqa
		"""Valida la nuova password."""
		message = psw_verify(field.data)
		if message:
			raise validators.ValidationError(message)

		message = psw_contain_usr(field.data, self.username.data)
		if message:
			raise validators.ValidationError(message)


class FormUserSignup(FlaskForm):
	"""Form dati signup account Utente."""
	username = StringField(
		'Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=40)], default=""
	)

	syd_user = StringField('User SYD', validators=[Length(min=3, max=25), Optional()])

	new_password_1 = PasswordField('Nuova Password', validators=[
		DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])
	new_password_2 = PasswordField('Conferma Password', validators=[
		DataRequired("Campo obbligatorio!"), Length(min=8, max=64),
		EqualTo('new_password_1',
		        message='Le due password inserite non corrispondono tra di loro. Riprova a inserirle!')])

	psw_changed = BooleanField('Password cambiata', default=False)

	name = StringField('Nome', validators=[Length(min=3, max=25), Optional()])
	last_name = StringField('Cognome', validators=[Length(min=3, max=25), Optional()])

	email = EmailField('email', validators=[DataRequired("Campo obbligatorio!"), Email(), Length(max=80)])
	phone = StringField('Telefono', validators=[Length(min=7, max=25), Optional()], default="+39 ")

	note = StringField('Read_for_migrate_db', validators=[Length(max=255), Optional()])

	submit = SubmitField("SIGNUP")

	def __repr__(self):
		return f'<USER SIGNUP with username: {self.username}>'

	def __str__(self):
		return f'<USER SIGNUP with username: {self.username}>'

	def validate_username(self, field):  # noqa
		"""Verifica presenza username nella tabella del DB."""
		if field.data in list_admin()[0]:
			raise ValidationError("Username già utilizzato in tabella amministratori.")
		if field.data in list_user()[0]:
			raise ValidationError("Username già utilizzato in tabella utenti.")

	def validate_email(self, field):  # noqa
		"""Verifica presenza email nella tabella del DB."""
		if field.data in list_admin()[1]:
			raise ValidationError("Email già utilizzata in tabella amministratori.")
		if field.data in list_user()[1]:
			raise ValidationError("Email già utilizzata in tabella utenti.")

	def validate_new_password_1(self, field):  # noqa
		"""Valida la nuova password."""
		message = psw_verify(field.data)
		if message:
			raise validators.ValidationError(message)

		message = psw_contain_usr(field.data, self.username.data)
		if message:
			raise validators.ValidationError(message)


class FormAccountUpdate(FlaskForm):
	"""Form di modifica dati account escluso password ed e-mail"""
	username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=40)])

	syd_user = StringField('User SYD', validators=[Length(min=3, max=25), Optional()])

	name = StringField('Nome', validators=[Length(min=3, max=25), Optional()])
	last_name = StringField('Cognome', validators=[Length(min=3, max=25), Optional()])

	email = EmailField('email', validators=[DataRequired("Campo obbligatorio!"), Email(), Length(max=80)])
	phone = StringField('Telefono', validators=[Length(min=7, max=25), Optional()])

	note = StringField('Read_for_migrate_db', validators=[Length(max=255)])

	submit = SubmitField("MODIFICA")

	def __repr__(self):
		return f'<UPDATE - username: {self.username}>'

	def __str__(self):
		return f'<UPDATE - username: {self.username}>'

	def to_dict(self):
		"""Converte form in dict."""
		return {
			'username': self.username.data,
			'name': self.name.data,
			'syd_user': self.syd_user.data,
			'last_name': self.last_name.data,
			'full_name': F"{self.name.data} {self.last_name.data}",
			'email': self.email.data,
			'phone': self.phone.data,
			'note': self.note.data,
		}


class FormUserResetPsw(FlaskForm):
	"""Form reset password utente."""
	email = EmailField('email', validators=[DataRequired("Campo obbligatorio!"), Email(), Length(max=80)])

	submit = SubmitField("MODIFICA")

	def __repr__(self):
		return f'<RESET PSW - email: {self.email}>'

	def __str__(self):
		return f'<RESET PSW - email: {self.email}>'

	def to_dict(self):
		"""Converte form in dict."""
		return {'email': self.email.data}
