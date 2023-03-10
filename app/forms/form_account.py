from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, validators, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional

from app.app import db
from app.models.accounts import Administrator, User
from app.utilitys.functions import not_empty
from app.utilitys.functions_accounts import psw_verify, psw_contain_usr


def list_admin():
	try:
		records = Administrator.query.all()
		_list = [x.to_dict() for x in records]

		_user = [d["username"] for d in _list if "username" in d]
		_email = [d["email"] for d in _list if "email" in d]

		db.session.close()
		return _user, _email
	except Exception as err:
		db.session.close()
		print('ERROR_LIST_ADMINISTRATORS:', err)
		return []


def list_user():
	try:
		records = User.query.all()
		_list = [x.to_dict() for x in records]

		_user = [d["username"] for d in _list if "username" in d]
		_email = [d["email"] for d in _list if "email" in d]

		db.session.close()
		return _user, _email
	except Exception as err:
		db.session.close()
		print('ERROR_LIST_USERS:', err)
		return []


class FormAdminSignup(FlaskForm):
	"""Form dati signup account Administrator."""
	username = StringField(
		'Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=20)], default="")

	new_password_1 = PasswordField('Nuova Password', validators=[
		DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])
	new_password_2 = PasswordField('Conferma Password', validators=[
		DataRequired("Campo obbligatorio!"), Length(min=8, max=64),
		EqualTo('new_password_1', message='Le password non corrispondono.')
	])

	psw_changed = BooleanField('Password cambiata')

	name = StringField('Nome', validators=[Optional(), Length(min=3, max=50)])
	last_name = StringField('Cognome', validators=[Optional(), Length(min=3, max=50)])

	email = EmailField('email', validators=[DataRequired("Campo obbligatorio!"), Email(), Length(max=80)])
	phone = StringField('Telefono', validators=[Optional(), Length(min=7, max=25)], default="+39 ")

	note = TextAreaField('Note', validators=[Optional(), Length(max=255)])

	submit = SubmitField("SIGNUP")

	def __repr__(self):
		return f'<ADMINISTRATOR SIGNUP with username: {self.username}>'

	def __str__(self):
		return f'<ADMINISTRATOR SIGNUP with username: {self.username}>'

	def validate_username(self, field):  # noqa
		"""Verifica presenza username nella tabella del DB."""
		if field.data in list_admin()[0]:
			raise ValidationError("Username gi?? utilizzato in tabella amministratori.")
		if field.data in list_user()[0]:
			raise ValidationError("Username gi?? utilizzato in tabella utenti.")

	def validate_email(self, field):  # noqa
		"""Verifica presenza email nella tabella del DB."""
		if field.data in list_admin()[1]:
			raise ValidationError("Email gi?? utilizzata in tabella amministratori.")
		if field.data in list_user()[1]:
			raise ValidationError("Email gi?? utilizzata in tabella utenti.")

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
		'Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=20)], default=""
	)

	# syd_user = StringField('User SYD', validators=[Length(min=3, max=25), Optional()])

	new_password_1 = PasswordField('Nuova Password', validators=[
		DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])
	new_password_2 = PasswordField('Conferma Password', validators=[
		DataRequired("Campo obbligatorio!"), Length(min=8, max=64),
		EqualTo('new_password_1',
				message='Le due password inserite non corrispondono tra di loro. Riprova a inserirle!')])

	psw_changed = BooleanField('Password cambiata')

	name = StringField('Nome', validators=[Optional(), Length(min=3, max=50)])
	last_name = StringField('Cognome', validators=[Optional(), Length(min=3, max=50)])

	email = EmailField('email', validators=[DataRequired("Campo obbligatorio!"), Email(), Length(max=80)])
	phone = StringField('Telefono', validators=[Optional(), Length(min=7, max=25)], default="+39 ")

	note = TextAreaField('Note', validators=[Optional(), Length(max=255)])

	submit = SubmitField("SIGNUP")

	def __repr__(self):
		return f'<USER SIGNUP with username: {self.username}>'

	def __str__(self):
		return f'<USER SIGNUP with username: {self.username}>'

	def validate_username(self, field):  # noqa
		"""Verifica presenza username nella tabella del DB."""
		if field.data in list_admin()[0]:
			raise ValidationError("Username gi?? utilizzato in tabella amministratori.")
		if field.data in list_user()[0]:
			raise ValidationError("Username gi?? utilizzato in tabella utenti.")

	def validate_email(self, field):  # noqa
		"""Verifica presenza email nella tabella del DB."""
		if field.data in list_admin()[1]:
			raise ValidationError("Email gi?? utilizzata in tabella amministratori.")
		if field.data in list_user()[1]:
			raise ValidationError("Email gi?? utilizzata in tabella utenti.")

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
	username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=20)])

	# syd_user = StringField('User SYD', validators=[Length(min=3, max=25), Optional()])

	name = StringField('Nome', validators=[Optional(), Length(min=3, max=50)])
	last_name = StringField('Cognome', validators=[Optional(), Length(min=3, max=50)])

	email = EmailField('email', validators=[DataRequired("Campo obbligatorio!"), Email(), Length(max=80)])
	phone = StringField('Telefono', validators=[Optional(), Length(min=7, max=25)])

	note = TextAreaField('Note', validators=[Optional(), Length(max=255)])

	submit = SubmitField("MODIFICA")

	def __repr__(self):
		return f'<UPDATE - username: {self.username}>'

	def __str__(self):
		return f'<UPDATE - username: {self.username}>'

	def to_dict(self):
		"""Converte form in dict."""
		name = self.name.data.strip().replace(" ", "")
		last_name = self.last_name.data.strip().replace("  ", " ")
		return {
			'username': self.username.data.strip().replace(" ", ""),
			# 'syd_user': self.syd_user.data.strip().replace(' ', ''),

			'name': name,
			'last_name': last_name,
			'full_name': f'{name} {last_name}',

			'email': self.email.data.strip().replace(" ", ""),
			'phone': not_empty(self.phone.data),

			'note': not_empty(self.note.data),
			'updated_at': datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
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
