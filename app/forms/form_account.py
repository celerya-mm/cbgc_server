from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional

from app.models.accounts import Administrator, User


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
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=40)])
    new_password_1 = PasswordField('Nuova Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])
    new_password_2 = PasswordField('Conferma Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64),
        EqualTo('new_password_1',
                message='Le due password inserite non corrispondono tra di loro. Riprova a inserirle!')])

    name = StringField('Nome', validators=[Length(min=3, max=25), Optional()])
    last_name = StringField('Cognome', validators=[Length(min=3, max=25), Optional()])

    email = EmailField('email', validators=[Email(), Length(max=80), Optional()])
    phone = StringField('Telefono', validators=[Length(min=7, max=25), Optional()], default="+39 ")

    note = StringField('Note', validators=[Length(max=255), Optional()])

    submit = SubmitField("SIGNUP")

    @staticmethod
    def validate_password(self):
        """Valida la nuova password."""
        if self.new_password_1.data != self.new_password_2.data:
            raise ValidationError('Passwords do not match')

    @staticmethod
    def validate_username(self, field):
        """Valida nuovo username."""
        if field.data in list_admin():
            raise ValidationError("E' già presente un AMMINISTRATORE con lo stesso username.")


class FormUserSignup(FlaskForm):
    """Form dati signup account Utente."""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=40)])
    new_password_1 = PasswordField('Nuova Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])
    new_password_2 = PasswordField('Conferma Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64),
        EqualTo('new_password_1',
                message='Le due password inserite non corrispondono tra di loro. Riprova a inserirle!')])

    name = StringField('Nome', validators=[Length(min=3, max=25), Optional()])
    last_name = StringField('Cognome', validators=[Length(min=3, max=25), Optional()])

    email = EmailField('email', validators=[Email(), Length(max=80), Optional()])
    phone = StringField('Telefono', validators=[Length(min=7, max=25), Optional()], default="+39 ")

    note = StringField('Note', validators=[Length(max=255), Optional()])

    submit = SubmitField("SIGNUP")

    @staticmethod
    def validate_password(self):
        """Valida la nuova password."""
        if self.new_password_1.data != self.new_password_2.data:
            raise ValidationError('Passwords do not match')

    @staticmethod
    def validate_username(self, field):
        """Valida nuovo username."""
        if field.data in list_user():
            raise ValidationError("E' già presente un UTENTE con lo stesso username.")


class FormAccountUpdate(FlaskForm):
    """Form di modifica dati account escluso password ed e-mail"""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=40)])

    name = StringField('Nome', validators=[Length(min=3, max=25), Optional()])
    last_name = StringField('Cognome', validators=[Length(min=3, max=25), Optional()])

    email = EmailField('email', validators=[Email(), Length(max=80), Optional()])
    phone = StringField('Telefono', validators=[Length(min=7, max=25), Optional()], default="+39 ")

    note = StringField('Note', validators=[Length(max=255), Optional()])

    submit = SubmitField("MODIFICA")
