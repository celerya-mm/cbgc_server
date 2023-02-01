from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, validators
from wtforms.validators import DataRequired, Email, Length, EqualTo

from app.utilitys.functions_accounts import psw_verify


class FormLogin(FlaskForm):
    """Form di login."""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired("Campo obbligatorio!"), Length(min=8)])

    submit = SubmitField("LOGIN")


class FormInsertMail(FlaskForm):
    """Form d'invio mail per reset password"""
    email = EmailField('Current e-mail', validators=[DataRequired("Campo obbligatorio!"), Email(), Length(max=80)])
    submit = SubmitField("SEND EMAIL")


class FormPswChange(FlaskForm):
    """Form per cambio password"""
    old_password = PasswordField('Current Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])

    new_password_1 = PasswordField('Nuova Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])
    new_password_2 = PasswordField('Conferma Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64),
        EqualTo('new_password_1', message='Le password non corrispondono.')
    ])

    submit = SubmitField("SEND_NEW_PASSWORD")

    def validate_new_password_1(self, field):  # noqa
        """Valida la nuova password."""
        message = psw_verify(field.data)
        if message:
            raise validators.ValidationError(message)


class FormPswReset(FlaskForm):
    """Form per reset password"""
    new_password_1 = PasswordField('Nuova Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])
    new_password_2 = PasswordField('Conferma Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64),
        EqualTo('new_password_1', message='Le password non corrispondono.')
    ])

    submit = SubmitField("SEND_NEW_PASSWORD")

    def validate_new_password_1(self, field):  # noqa
        """Valida la nuova password."""
        message = psw_verify(field.data)
        if message:
            raise validators.ValidationError(message)
