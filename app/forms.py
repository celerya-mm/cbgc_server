from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, SelectField, validators
from wtforms.validators import DataRequired, Length


class FormLogin(FlaskForm):
    """Form di login."""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired("Campo obbligatorio!"), Length(min=8)])

    submit = SubmitField("LOGIN")


class FormAccountSignup(FlaskForm):
    """Form dati signup account Administrator."""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    password1 = PasswordField('Password1', validators=[DataRequired("Campo obbligatorio!"), Length(min=8)])
    password2 = PasswordField('Password2', validators=[
        DataRequired("Campo obbligatorio!"),  Length(min=8),
        validators.EqualTo('password1', message='Le password non corrispondono!')
    ])
    name = StringField('First Name', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    last_name = StringField('First Name', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    email = EmailField('email', validators=[DataRequired("Campo obbligatorio!")])

    submit = SubmitField("SIGNUP")


class AccountUpdateForm(FlaskForm):
    """Form di modifica dati account escluso password ed e-mail"""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    name = StringField('First Name', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    last_name = StringField('First Name', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    email = EmailField('email', validators=[DataRequired("Campo obbligatorio!")])

    submit = SubmitField("MODIFICA")


class SignUpForm(FlaskForm):
    """Form di SgnUp"""
    username = StringField(
        'Username',
        validators=[
            DataRequired("Campo obbligatorio!"),
            Length(min=3)
        ]
    )
    email = EmailField(
        'e-mail',
        validators=[
            DataRequired("Campo obbligatorio!"),
        ]
    )
    password1 = PasswordField(
        'Password1',
        validators=[
            DataRequired("Campo obbligatorio!"),
            Length(min=8)
        ]
    )
    password2 = PasswordField(
        'Password2',
        validators=[
            DataRequired("Campo obbligatorio!"),
            Length(min=8),
            validators.EqualTo('password1', message='le password non corrispondono')
        ]
    )
    first_name = StringField(
        'First Name',
        validators=[
            DataRequired("Campo obbligatorio!"),
            Length(min=3)
        ]
    )
    last_name = StringField(
        'Last Name',
        validators=[
            DataRequired("Campo obbligatorio!"),
            Length(min=3)
        ]
    )
    pubkey = StringField(
        'Public Key',
        validators=[
            DataRequired("Campo obbligatorio!"),
            Length(min=782, max=800)
        ]
    )
    timezone = SelectField(
        'Time Zone',
        default='Europe/Rome',
        choices=("Europe/Rome"),
        validators=[
            DataRequired("Campo obbligatorio!"),
            Length(min=8, max=40)
        ]
    )
    vat_id = StringField(
        'Vat number',
        validators=[
            DataRequired("Campo obbligatorio!"),
            Length(min=11, max=13)
        ]
    )
    pec_email = EmailField(
        'Pec',
        validators=[
            DataRequired("Campo obbligatorio!"),
        ]
    )
    sdi_code = StringField(
        'SDI code',
        validators=[
            DataRequired("Campo obbligatorio!"),
            Length(min=6, max=7)
        ]
    )
    submit = SubmitField("SIGNUP")


class insertMailForm(FlaskForm):
    """Form d'invio mail per cambio password"""
    email = EmailField(
        'Current e-mail',
        validators=[
            DataRequired("Campo obbligatorio!"),
        ]
    )
    submit = SubmitField("SEND EMAIL")


class pswChangeForm(FlaskForm):
    old_password = PasswordField(
        'Old_Password',
        validators=[
            DataRequired("Campo obbligatorio!"),
            Length(min=8)
        ]
    )
    password1 = PasswordField(
        'Password1',
        validators=[
            DataRequired("Campo obbligatorio!"),
            Length(min=8)
        ]
    )
    password2 = PasswordField(
        'Password2',
        validators=[
            DataRequired("Campo obbligatorio!"),
            Length(min=8),
            validators.EqualTo('password1', message='le password non corrispondono')
        ]
    )
    submit = SubmitField("SEND NEW PASSWORD")
