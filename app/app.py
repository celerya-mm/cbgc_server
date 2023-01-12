import secrets
from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_misaka import Misaka

db = SQLAlchemy()

app = Flask(__name__, instance_relative_config=False)
app.config.from_object(Config)

secret = secrets.token_urlsafe(32)
app.secret_key = secret

# formattazione avanzata del testo
Misaka(app)

db.init_app(app)

with app.app_context():
    from app import routes
    from app.api import (api_administrators,
                         api_users,
                         api_farmers,
                         api_buyers,
                         api_heads,
                         api_slaughterhouses,
                         api_certificates_cons,
                         api_certificates_dna)
    from app.models import (accounts,
                            farmers,
                            buyers,
                            certificates_dna,
                            certificates_cons,
                            slaughterhouses,
                            heads,
                            tokens)

    db.create_all()
