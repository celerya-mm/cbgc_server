from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import \
    PasswordField, \
    StringField, \
    SubmitField, \
    EmailField, \
    SelectField, \
    validators, \
    DateField, \
    BooleanField

from wtforms.validators import DataRequired, Email, Length, EqualTo


class FormLogin(FlaskForm):
    """Form di login."""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired("Campo obbligatorio!"), Length(min=8)])

    submit = SubmitField("LOGIN")


class FormAccountSignup(FlaskForm):
    """Form dati signup account Administrator."""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    new_password_1 = PasswordField('New Password', validators=[DataRequired("Campo obbligatorio!"), Length(min=8)])
    new_password_2 = PasswordField('Password Confirm', validators=[
        DataRequired("Campo obbligatorio!"),  Length(min=8),
        EqualTo('new_password_1', message='Both password fields must be equal!')
    ])
    name = StringField('First Name', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    last_name = StringField('Last Name', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    email = EmailField('email', validators=[DataRequired("Campo obbligatorio!"), Email()])
    phone = StringField('Telefono', validators=[Length(min=7)])

    submit = SubmitField("SIGNUP")

    def validate_password(self):
        if self.new_password_1.data != self.new_password_2.data:
            raise validators.ValidationError('Passwords do not match')


class FormAccountUpdate(FlaskForm):
    """Form di modifica dati account escluso password ed e-mail"""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    name = StringField('Nome', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    last_name = StringField('Cognome', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    email = EmailField('email', validators=[DataRequired("Campo obbligatorio!"), Email()])
    phone = StringField('Telefono', validators=[Length(min=7)])

    submit = SubmitField("MODIFICA")


class FormFarmerCreate(FlaskForm):
    """Form dati signup account Administrator."""
    farmer_name = StringField('Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    email = EmailField('Email', validators=[DataRequired("Campo obbligatorio!"), Email()])
    phone = StringField('Telefono', validators=[DataRequired("Campo obbligatorio!"), Length(min=7)])

    affiliation_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())
    affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"], default="NO")

    stable_code = StringField('Codice Stalla')
    stable_type = SelectField("Tipo Stalla", choices=["Allevamento", "Stalla di sosta"], default="Allevamento")
    stable_productive_orientation = SelectField("Orientamento Produttivo", choices=[
        "Da Latte", "Da Carne", "Da Latte e Da Carne"], default="Da Carne")
    stable_breeding_methods = SelectField("modalità Allevamento", choices=[
        "Estensivo", "Intensivo", "Transumante", "Brado"], default="Estensivo")

    address = StringField('Indirizzo', validators=[DataRequired("Campo obbligatorio!"), Length(min=5)])
    cap = StringField('CAP', validators=[DataRequired("Campo obbligatorio!"), Length(min=5, max=5)])
    city = StringField('Città', validators=[DataRequired("Campo obbligatorio!"), Length(min=5)])

    submit = SubmitField("CREATE")


class FormInsertMail(FlaskForm):
    """Form d'invio mail per cambio password"""
    email = EmailField('Current e-mail', validators=[DataRequired("Campo obbligatorio!"), Email()])
    submit = SubmitField("SEND EMAIL")


class FormPswChange(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired("Campo obbligatorio!"), Length(min=8)])
    new_password_1 = PasswordField('New Password', validators=[DataRequired("Campo obbligatorio!"), Length(min=8)])
    new_password_2 = PasswordField('Password Confirm', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8),
        EqualTo('new_password_1', message='Both password fields must be equal!')
    ])
    submit = SubmitField("SEND_NEW_PASSWORD")

    def validate_password(self):
        if self.new_password_1.data != self.new_password_2.data:
            raise validators.ValidationError('Passwords do not match')
