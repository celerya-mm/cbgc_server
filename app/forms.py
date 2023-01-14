from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, SelectField, validators
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

    submit = SubmitField("SIGNUP")

    def validate_password(self):
        if self.new_password_1.data != self.new_password_2.data:
            raise validators.ValidationError('Passwords do not match')


class FormAccountUpdate(FlaskForm):
    """Form di modifica dati account escluso password ed e-mail"""
    username = StringField('Username', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    name = StringField('First Name', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    last_name = StringField('Last Name', validators=[DataRequired("Campo obbligatorio!"), Length(min=3)])
    email = EmailField('email', validators=[DataRequired("Campo obbligatorio!"), Email()])

    submit = SubmitField("MODIFICA")


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
