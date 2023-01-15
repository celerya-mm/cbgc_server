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
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=40)])
    new_password_1 = PasswordField('Nuova Password', validators=[
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64)])
    new_password_2 = PasswordField('Conferma Password', validators=[
        DataRequired("Campo obbligatorio!"),  Length(min=8, max=64),
        EqualTo('new_password_1',
                message='Le due password inserite non corrispondono tra di loro. Riprova a inserirle!')])

    name = StringField('Nome', validators=[Length(min=3, max=25)])
    last_name = StringField('Cognome', validators=[Length(min=3, max=25)])
    email = EmailField('email', validators=[Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=25)])

    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("SIGNUP")

    def validate_password(self):
        """Valida la nuova password."""
        if self.new_password_1.data != self.new_password_2.data:
            raise validators.ValidationError('Passwords do not match')


class FormAccountUpdate(FlaskForm):
    """Form di modifica dati account escluso password ed e-mail"""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=40)])

    name = StringField('Nome', validators=[Length(min=3, max=25)])
    last_name = StringField('Cognome', validators=[Length(min=3, max=25)])
    email = EmailField('email', validators=[Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=25)])

    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("MODIFICA")


class FormFarmer(FlaskForm):
    """Form dati signup account Administrator."""
    farmer_name = StringField('Ragione Sociale', validators=[
        DataRequired("Campo obbligatorio!"),
        Length(min=3, max=100)])

    email = EmailField('Email', validators=[Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=80)])
    address = StringField('Indirizzo', validators=[Length(min=5, max=255)])
    cap = StringField('CAP', validators=[Length(min=5, max=5)])
    city = StringField('Città', validators=[Length(min=3, max=55)])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())
    affiliation_end_date = DateField('Cessazione affiliazione', format='%Y-%m-%d')
    affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"], default="NO")

    stable_code = StringField('Codice Stalla', validators=[Length(min=3, max=25)])
    stable_type = SelectField("Tipo Stalla", choices=["Allevamento", "Stalla di sosta"], default="Allevamento")
    stable_productive_orientation = SelectField("Orientamento Produttivo", choices=[
        "Da Latte", "Da Carne", "Da Latte e Da Carne"], default="Da Carne")
    stable_breeding_methods = SelectField("Modalità Allevamento", choices=[
        "Estensivo", "Intensivo", "Transumante", "Brado"], default="Estensivo")

    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")


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
