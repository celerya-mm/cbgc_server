import os
import secrets  # noqa

from flask import Flask, session  # noqa
from flask_caching import Cache
from flask_mail import Mail, Message  # noqa
from flask_migrate import Migrate
from flask_misaka import Misaka
from flask_session import Session

from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config, db

PATH_PROJECT = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__, instance_relative_config=False)

# imposto app dietro reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# carico parametri configurazione
app.config.from_object(Config)

# imposto la cache per l'app (simple_cache, time_out=3600s)
cache = Cache(app)

# secret = secrets.token_urlsafe(32)
app.secret_key = Config.SECRET_KEY

# imposta invio mail
mail = Mail(app)

# formattazione avanzata del testo
Misaka(app)

# imposta sessione browser per server gunicorn
Session(app)

# impostazioni DB
db.init_app(app)

migrate = Migrate(app, db)
migrate.init_app(app, db)

with app.app_context():
	from app.api import (api_administrators, api_buyers, api_certificates_cons, api_certificates_dna,  # noqa
	                     api_farmers, api_heads, api_slaughterhouses, api_users)
	from app.models import (accounts, buyers, certificates_dna, certificates_cons, events_db, farmers, heads,  # noqa
							slaughterhouses, auth_tokens)
	from app.routes import (routes, routes_admin, routes_buyer, routes_head, routes_farmer, routes_event,  # noqa
	                        routes_slaughterhouse, routes_user, routes_cert_dna, routes_cert_cons)
