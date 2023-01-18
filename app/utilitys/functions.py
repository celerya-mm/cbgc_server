import json
from ast import literal_eval
from datetime import datetime
from functools import wraps

import requests
from flask import flash, session, url_for, redirect
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from app.app import db
from app.models.events_db import EventDB
from app.models.tokens import AuthToken
from app.var_ambient import variables as var

disable_warnings(InsecureRequestWarning)


def url_to_json(_str, val_date=None):
    """Converte stringa passata da url in json."""
    try:
        _str = literal_eval(_str)
    except ValueError:
        _str = _str \
            .replace("{'", '{"').replace("'}", '"}') \
            .replace(": '", ': "').replace("':", '":') \
            .replace(", '", ', "').replace("',", '",')

        if val_date:
            _list_field = []
            for x in val_date:
                _list_field.append(val_date[x])
            # print("LISTA_CAMPI_DATA:", _list_field)

            for d in _list_field:
                if f'"{d}": datetime.datetime' in _str:
                    # print("SELECT:", f'"{d}": datetime.datetime')
                    _split = _str.split(f'"{d}": datetime.datetime')[1]
                    # print("STR_SPLIT:", _split)
                    _split = str(_split.split(', "')[0])
                    # print("STR_DATETIME:", _split)
                    _replace = f"datetime.datetime{_split}"
                    # print("REPLACE:", _replace)
                    _split = _split.replace('(', "").replace(')', "").split(', ')
                    # print("LIST_DATETIME:", _split)
                    date = f"{_split[0]}-{_split[1]}-{_split[2]}"
                    # print("DATETIME:", date)
                    _str = _str.replace(_replace, f'"{date}"')
                    # print("STR:", _str)

        _str = literal_eval(_str)
    # print("URL_WORK:", _str, "TYPE:", type(_str))
    # print("URL_TO_JSON:", json.dumps(_str, indent=2), "TYPE:", type(_str))
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


def token_admin_validate(func):
    """Eseguo la funzione solo se presente token autenticazione valido."""
    @wraps(func)
    def wrap(*args, **kwargs):
        if "token_login" in session.keys() or session["token_login"]:
            # controlla validità token
            authenticated = AuthToken.query.filter_by(token=session["token_login"]).first()
            if authenticated is None:
                flash(f"There is no authenticated log-in with your username. "
                      f"Please log-in again with an administrator account.")
                return redirect(url_for('logout'))
            elif authenticated.expires_at < datetime.now():
                flash("Your authenticated log-in is expired. "
                      "Please log-in again with an administrator account.")
                return redirect(url_for('logout'))
            elif authenticated.admin_id in ["", None]:
                flash(f"Your account {authenticated.admin_id} does not allow this operation. "
                      f"Please log-in with an administrator account.")
                return redirect(url_for('logout'))
            else:
                # esegue la funzione
                return func(*args, **kwargs)
        else:
            flash(f"Token autenticazione non presente, devi eseguire la Log-In.")
            return redirect(url_for('logout'))
    return wrap


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


def address_mount(address, cap, city):
    """Monta indirizzo completo."""
    if address and cap and city:
        full_address = f"{address} - {cap} - {city}"
    elif address and cap:
        full_address = f"{address} - {cap}"
    elif address and city:
        full_address = f"{address} - {city}"
    elif cap and city:
        full_address = f"{cap} - {city}"
    elif address:
        full_address = address
    elif city:
        full_address = city
    elif cap:
        full_address = cap
    else:
        full_address = None

    return full_address


def year_extract(date):
    """Estrae l'anno da una data"""
    if date:
        print("TYPE_DATA", type(date))
        year = datetime.strptime(date, "%Y-%m-%d")
        return year.year
    else:
        return None
