import secrets

from flask import Flask
from flask_migrate import Migrate
from flask_misaka import Misaka
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__, instance_relative_config=False)
app.config.from_object(Config)

secret = secrets.token_urlsafe(32)
app.secret_key = secret

# formattazione avanzata del testo
Misaka(app)

db = SQLAlchemy()
migrate = Migrate(app, db)

db.init_app(app)
migrate.init_app(app, db)

with app.app_context():
    from app import routes_admin
    from app.api import (
        api_administrators,
        api_users,
        api_farmers,
        api_buyers,
        api_heads,
        api_slaughterhouses,
        api_certificates_cons,
        api_certificates_dna
    )
    from app.models import (
        accounts,
        farmers,
        buyers,
        certificates_dna,
        certificates_cons,
        slaughterhouses,
        heads,
        tokens,
        events_db
    )

    # db.reflect()  # Verifica tabelle presenti nel DB.
    # db.drop_all()  # Attenzione elimina tutte le tabelle dal DB.
    db.create_all()  # Crea le tabelle nel DB
