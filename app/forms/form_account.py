from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, validators
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from ..models.accounts import Administrator, User


def list_admin():
    records = Administrator.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["username"] for d in _list if "username" in d]
    return _list


def list_user():
    records = User.query.all()
    _list = [x.to_dict() for x in records]
    _list = [d["username"] for d in _list if "username" in d]
    return _list


class FormAdminSignup(FlaskForm):
    """Form dati signup account Administrator."""
    username = StringField(
        'Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=40)], default="")

    new_password_1 = PasswordField('Nuova Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])
    new_password_2 = PasswordField('Conferma Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64),
        EqualTo('new_password_1',
                message='Le due password inserite non corrispondono tra di loro. Riprova a inserirle!')])

    name = StringField('Nome', validators=[Length(min=3, max=25)])
    last_name = StringField('Cognome', validators=[Length(min=3, max=25)])

    email = EmailField('email', validators=[Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=25)], default="+39 ")

    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("SIGNUP")

    def __repr__(self):
        return f'<ADMINISTRATOR SIGNUP with username: {self.username}>'

    def __str__(self):
        return f'<ADMINISTRATOR SIGNUP with username: {self.username}>'

    def validate_password(self):
        """Valida la nuova password."""
        if self.new_password_1.data != self.new_password_2.data:
            raise validators.ValidationError('Passwords do not match')

    def validate_username(self, field):  # noqa
        if field.data in list_admin():
            raise ValidationError("E' già presente un AMMINISTRATORE con lo stesso username.")


class FormUserSignup(FlaskForm):
    """Form dati signup account Utente."""
    username = StringField(
        'Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=40)], default="")
    new_password_1 = PasswordField('Nuova Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])
    new_password_2 = PasswordField('Conferma Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64),
        EqualTo('new_password_1',
                message='Le due password inserite non corrispondono tra di loro. Riprova a inserirle!')])

    name = StringField('Nome', validators=[Length(min=3, max=25)])
    last_name = StringField('Cognome', validators=[Length(min=3, max=25)])

    email = EmailField('email', validators=[Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=25)], default="+39 ")

    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("SIGNUP")

    def __repr__(self):
        return f'<USER SIGNUP with username: {self.username}>'

    def __str__(self):
        return f'<USER SIGNUP with username: {self.username}>'

    def validate_password(self):
        """Valida la nuova password."""
        if self.new_password_1.data != self.new_password_2.data:
            raise validators.ValidationError('Passwords do not match')

    def validate_username(self, field):  # noqa
        if field.data in list_user():
            raise ValidationError("E' già presente un UTENTE con lo stesso username.")


class FormAccountUpdate(FlaskForm):
    """Form di modifica dati account escluso password ed e-mail"""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=40)])

    name = StringField('Nome', validators=[Length(min=3, max=25)])
    last_name = StringField('Cognome', validators=[Length(min=3, max=25)])

    email = EmailField('email', validators=[DataRequired("Campo obbligatorio!"), Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=25)])

    note = StringField('Note', validators=[Length(max=255)])

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
            'last_name': self.last_name.data,
            'full_name': F"{self.name.data} {self.last_name.data}",
            'email': self.email.data,
            'phone': self.phone.data,
            'note': self.note.data,
        }

    def to_db(self):
        """Converte form in dict."""
        return {
            'username': self.username.data,
            'name': self.name.data,
            'last_name': self.last_name.data,
            'full_name': F"{self.name.data} {self.last_name.data}",
            'email': self.email.data,
            'phone': self.phone.data,
            'note': self.note.data,
        }
