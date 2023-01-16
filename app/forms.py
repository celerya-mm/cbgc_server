from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import (PasswordField, StringField, SubmitField, EmailField, SelectField, validators, DateField,
                     IntegerField, FloatField)
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from app.models.accounts import User, Administrator  # noqa
from app.models.buyers import Buyer
from app.models.certificates_cons import CertificateCons
from app.models.certificates_dna import CertificateDna  # noqa
from app.models.events_db import EventDB  # noqa
from app.models.farmers import Farmer
from app.models.heads import Head
from app.models.slaughterhouses import Slaughterhouse
from app.models.tokens import AuthToken  # noqa


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
        DataRequired("Campo obbligatorio!"), Length(min=8, max=64),
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
    """Form inserimento dati Allevatore."""
    farmer_name = StringField('Ragione Sociale', validators=[
        DataRequired("Campo obbligatorio!"),
        Length(min=3, max=100)])

    email = EmailField('Email', validators=[Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=80)])

    address = StringField('Indirizzo', validators=[Length(min=5, max=255)])
    cap = StringField('CAP', validators=[Length(min=5, max=5)])
    city = StringField('Città', validators=[Length(min=3, max=55)])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())

    stable_code = StringField('Codice Stalla', validators=[Length(min=3, max=25)])
    stable_type = SelectField("Tipo Stalla", choices=["Allevamento", "Stalla di sosta"], default="Allevamento")
    stable_productive_orientation = SelectField("Orientamento Produttivo", choices=[
        "Da Latte", "Da Carne", "Da Latte e Da Carne"], default="Da Carne")
    stable_breeding_methods = SelectField("Modalità Allevamento", choices=[
        "Estensivo", "Intensivo", "Transumante", "Brado"], default="Estensivo")

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")


class FormEndAffiliation(FlaskForm):
    """Inserisce data cessazione affiliazione."""
    farmer_name = StringField('Ragione Sociale')
    affiliation_end_date = DateField('Cessazione affiliazione', format='%Y-%m-%d', default=datetime.now())
    affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"], default="SI")


class FormBuyer(FlaskForm):
    """Form inserimento dati Acquirente."""
    buyer_name = StringField(
        'Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=100)]
    )

    buyer_type = SelectField("Tipo Acquirente", choices=["Macelleria", "Macello", "Ristorante"], default="Ristorante")

    email = EmailField('Email', validators=[Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=80)])

    address = StringField('Indirizzo', validators=[Length(min=5, max=255)])
    cap = StringField('CAP', validators=[Length(min=5, max=5)])
    city = StringField('Città', validators=[Length(min=3, max=55)])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())
    affiliation_end_date = DateField('Cessazione affiliazione', format='%Y-%m-%d')
    affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"], default="NO")

    users_list = []
    users = User.query.all()
    for user in users:
        users_list.append(user.username)

    user_id = SelectField("Utente Servizio", choices=users_list, default="")

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")


class FormSlaughterhouse(FlaskForm):
    """Form inserimento dati Macello."""
    slaughterhouse = StringField(
        'Ragione Sociale', validators=[DataRequired("Campo obbligatorio!"), Length(min=3, max=100)]
    )

    slaughterhouse_code = StringField('Codice Macello', validators=[Length(min=3, max=20)])

    email = EmailField('Email', validators=[Email(), Length(max=80)])
    phone = StringField('Telefono', validators=[Length(min=7, max=80)])

    address = StringField('Indirizzo', validators=[Length(min=5, max=255)])
    cap = StringField('CAP', validators=[Length(min=5, max=5)])
    city = StringField('Città', validators=[Length(min=3, max=55)])

    affiliation_start_date = DateField('Data affiliazione', format='%Y-%m-%d', default=datetime.now())
    affiliation_end_date = DateField('Cessazione affiliazione', format='%Y-%m-%d')
    affiliation_status = SelectField("Affiliazione", choices=["SI", "NO"], default="NO")

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")


class FormHead(FlaskForm):
    """Form inserimento dati Capo."""
    headset = StringField('Auricolare', validators=[DataRequired("Campo obbligatorio!"), Length(min=14, max=14)])

    birth_date = DateField('Data Nascita', format='%Y-%m-%d', default=datetime.now())
    castration_date = DateField('Data Castrazione', format='%Y-%m-%d', default="")
    slaughter_date = DateField('Data Macellazione', format='%Y-%m-%d', default="")
    sale_date = DateField('Data Vendita', format='%Y-%m-%d', default="")

    farmers_list = []
    farmers = Farmer.query.all()
    for f in farmers:
        farmers_list.append(f.farmer_name)
    farmer_id = SelectField("Seleziona Allevatore", choices=farmers_list, default="")

    slaughterhouses_list = []
    slaughterhouses = Slaughterhouse.query.all()
    for s in slaughterhouses:
        slaughterhouses_list.append(s.slaughterhouse)
    slaughterhouse_id = SelectField("Seleziona Macello", choices=slaughterhouses_list, default="")

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")


class FormCertCons(FlaskForm):
    """Form inserimento dati Certificato Consorzio."""
    # Estraggo lista records certificati e seleziono l'ultimo
    certificates = CertificateCons.query.all()
    old = max(certificates, key=lambda x: x.id)

    # Calcolo il nuo ID.
    today = datetime.now()
    if today.month >= 7 > old.certificate_date.month and today.year == old.certificate_date.year:
        new_id = 1
    elif old.certificate_date.month < 7 and today.year > old.certificate_date.year:
        new_id = 1
    else:
        new_id = old.certificate_id + 1
    certificate_id = IntegerField('ID', validators=[DataRequired("Campo obbligatorio!")], default=new_id)

    certificate_var = StringField('Integrazione ID', validators=[Length(max=10)])
    certificate_date = DateField('Data Certificato', format='%Y-%m-%d', default=datetime.now())

    cockade_id = IntegerField('ID Coccarda', default=new_id)
    cockade_var = StringField('Integrazione ID Coccarda', validators=[Length(max=10)])

    sale_type = SelectField(
        "Tipo Vendita", validators=[DataRequired("Campo obbligatorio!")],
        choices=["Capo intero", "Mezzena", "Parti Anatomiche"], default=""
    )
    sale_quantity = FloatField("Quantità Venduta (kg)")

    invoice_nr = StringField('Fattura NR', validators=[Length(max=20)])
    invoice_date = DateField('Fattura Data', format='%Y-%m-%d', default=datetime.now())
    invoice_status = SelectField(
        'Fattura Stato', validators=[DataRequired("Campo obbligatorio!")], choices=[
            "Da Emettere", "Emessa", "Annullata", "Non Pagata", "Pagata"
        ], default="Da Emettere"
    )

    farmers_list = []
    farmers = Farmer.query.all()
    for f in farmers:
        farmers_list.append(f.farmer_name)
    farmer_id = SelectField("Seleziona Allevatore", choices=farmers_list, default="")

    slaughterhouses_list = []
    slaughterhouses = Slaughterhouse.query.all()
    for s in slaughterhouses:
        slaughterhouses_list.append(s.slaughterhouse)
    slaughterhouse_id = SelectField("Seleziona Macello", choices=slaughterhouses_list, default="")

    buyer_list = []
    buyers = Buyer.query.all()
    for b in buyers:
        buyer_list.append(b.buyer_name)
    buyer_id = SelectField("Seleziona Acquirente", choices=buyer_list, default="")

    head_list = []
    heads = Head.query.all()
    for h in heads:
        head_list.append(h.headset)
    head_id = SelectField("Seleziona Capo", choices=head_list, default="")

    note_certificate = StringField('Note Certificato', validators=[Length(max=255)])
    note = StringField('Note', validators=[Length(max=255)])

    submit = SubmitField("CREATE")


class FormCertDNA(FlaskForm):
    """Form inserimento dati Certificato DNA."""
    dna_cert_id = StringField('ID', validators=[DataRequired("Campo obbligatorio!"), Length(max=20)])
    dna_cert_date = DateField(
        'Data Certificato', format='%Y-%m-%d', default=datetime.now(),
        validators=[DataRequired("Campo obbligatorio!"), Length(max=20)]
    )

    invoice_nr = StringField('Fattura NR', validators=[Length(max=20)])
    invoice_date = DateField('Fattura Data', format='%Y-%m-%d', default=datetime.now())
    invoice_status = SelectField(
        'Fattura Stato', validators=[DataRequired("Campo obbligatorio!")], choices=[
            "Da Emettere", "Emessa", "Annullata", "Non Pagata", "Pagata"
        ], default="Da Emettere"
    )

    farmers_list = []
    farmers = Farmer.query.all()
    for f in farmers:
        farmers_list.append(f.farmer_name)
    farmer_id = SelectField("Seleziona Allevatore", choices=farmers_list, default="")

    head_list = []
    heads = Head.query.all()
    for h in heads:
        head_list.append(h.headset)
    head_id = SelectField("Seleziona Capo", choices=head_list, default="")

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
