import json
from ast import literal_eval
from datetime import datetime

import requests
from flask import flash, session
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from app.app import db
from app.models.events_db import EventDB
from app.models.tokens import AuthToken
from app.var_ambient import variables as var

disable_warnings(InsecureRequestWarning)


def url_to_json(_str):
    """Converte stringa passata da url in json."""
    _str = literal_eval(_str)
    # print("LEV:", json.dumps(_str, indent=2), "TYPE:", type(_str))
    return _str


def event_create(event, admin_id=None, user_id=None, farmer_id=None, buyer_id=None,
                 slaughterhouse_id=None, head_id=None, cert_cons_id=None, cert_dna_id=None):
    """Registro evento DB."""
    try:
        new_event = EventDB(
            event=event,
            admin_id=admin_id,
            user_id=user_id,
            farmer_id=farmer_id,
            buyer_id=buyer_id,
            slaughterhouse_id=slaughterhouse_id,
            head_id=head_id,
            cert_cons_id=cert_cons_id,
            cert_dna_id=cert_dna_id
        )

        db.session.add(new_event)
        db.session.commit()
        print("EVENT_CREATED.")
        return True
    except Exception as err:
        print("ERROR_REGISTR_EVENT:", err)
        return False


def token_user_validate(_token):
    """Valido il token ricevuto."""
    authenticated = AuthToken.query.filter_by(token=_token).first()
    if authenticated in ["", None] or authenticated.expires_at < datetime.now() or authenticated.user_id in ["", None]:
        flash("You don't have a valid authentication token, please log in.")
        return False
    else:
        return True


def token_admin_validate():
    """Eseguo la funzione solo."""
    try:
        token = session["token_login"]
        if token:
            authenticated = AuthToken.query.filter_by(token=session["token_login"]).first()
            if authenticated is None:
                flash(f"There is no authenticated log in for your username. "
                      f"Please log in again with an administrator account.")
                return False
            elif authenticated.expires_at < datetime.now():
                flash("Your authenticated log in is expired. "
                      "Please log in again with an administrator account.")
                return False
            elif authenticated.admin_id in ["", None]:
                flash(f"Your account {authenticated.admin_id} does not allow this operation. "
                      f"Please log in with an administrator account.")
                return False
            else:
                return True
    except Exception as err:
        flash(f"Token autenticazione non presente, devi eseguire la Log-In. Errore: {err}")
        return False


def admin_log_in(form):
    """API - Login e ottengo il token."""
    url = var.apiUrls_admin["admin_login"]
    payload = json.dumps({"username": form.username.data, "password": form.password.data})
    print("PAYLOAD:", json.dumps(payload, indent=2))
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    try:
        print("RESPONSE:", response.text)
        _resp = json.loads(response.text)
        return _resp["data"]["token"]
    except Exception as err:
        print(f"ERRORE_RISPOSTA_SERVER: {err}")
        return False


def user_log_in(form):
    """API - Login e ottengo il token."""
    url = var.apiUrls_user["user_login"]
    payload = json.dumps({"username": form.username.data, "password": form.password.data})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    print("RESPONSE:", response.text)
    dati = json.loads(response.text)
    try:
        # dati = json.loads(response.text)
        return dati["token"]
    except Exception as err:
        print(f"ERRORE_RISPOSTA_SERVER: {err}")
        return False

# def farmers_list():
#     """API - Estraggo la lista di tutti gli allevatori."""
#     url = var.apiUrls["farmers_list"]
#     payload = ""
#     headers = {}
#     response = requests.request("GET", url, headers=headers, data=payload)
#     print("RESPONSE:", response.text)
#     dati = json.loads(response.text)
#     return response
#
#
# _farmers_list = farmers_list()
