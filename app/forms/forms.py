from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, SelectField, validators, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


class FormLogin(FlaskForm):
    """Form di login."""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired("Campo obbligatorio!"), Length(min=8)])

    submit = SubmitField("LOGIN")


class FormAffiliationChange(FlaskForm):
    """Inserisce data cessazione affiliazione."""
    name = StringField('Ragione Sociale')
    affiliation_end_date = DateField('Cessazione Affiliazione', format='%Y-%m-%d', default=datetime.now())
    affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"], default="SI")
    submit = SubmitField("CHANGE")

    def validate_affiliation_status(self, field):
        if field.data == "SI" and self.affiliation_end_date.data:
            raise ValidationError('Attenzione se è presente una data di cessazione lo Stato Affiliazione '
                                  'non può essere "SI".')


class FormInsertMail(FlaskForm):
    """Form d'invio mail per cambio password"""
    email = EmailField('Current e-mail', validators=[DataRequired("Campo obbligatorio!"), Email()])
    submit = SubmitField("SEND EMAIL")


class FormPswChange(FlaskForm):
    old_password = PasswordField('Current Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])

    new_password_1 = PasswordField('Nuova Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])
    new_password_2 = PasswordField('Conferma Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64),
        EqualTo('new_password_1',
                message='Le due password inserite non corrispondono tra di loro. Riprova a inserirle!')])

    submit = SubmitField("SEND_NEW_PASSWORD")

    def validate_password(self):
        if self.new_password_1.data != self.new_password_2.data:
            raise validators.ValidationError('Passwords do not match')
