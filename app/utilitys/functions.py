import json
from datetime import datetime, date
from functools import wraps

import requests
from flask import flash, session, url_for, redirect
from jinja2.utils import htmlsafe_json_dumps
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from ..app import db
from ..models.events_db import EventDB
from ..models.tokens import AuthToken
from ..var_ambient import variables as var

disable_warnings(InsecureRequestWarning)


def url_to_json(dict_obj):
    """Converte l'oggetto dict in una stringa JSON"""
    for k, v in dict_obj.items():
        dict_obj[k] = str(v).replace("/", "-")
    new_dict = dict_obj.copy()
    return htmlsafe_json_dumps(new_dict)


def json_loads_replace_none(dict_obj):
    """Rimpiazza 'None' con None in una stringa da convertire in json."""
    print("SONO DENTRO")
    for k, v in dict_obj.items():
        if v == "None":
            dict_obj[k] = None
        if v == "True":
            dict_obj[k] = True
        if v == "False":
            dict_obj[k] = False
    new_dict = dict_obj.copy()
    print("NEW_DICT:", new_dict, type(new_dict))
    return new_dict


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


def mount_full_name(name, last_name):
    """Monta il nome completo."""
    if name is not None and last_name is not None:
        full_name = f"{name} {last_name}"
    elif name is not None and last_name is None:
        full_name = name
    elif name is None and last_name is not None:
        full_name = last_name
    else:
        full_name = None
    return full_name


def year_extract(date):  # noqa
    """Estrae l'anno da una data"""
    if isinstance(date, str):
        year = datetime.strptime(date, "%Y-%m-%d")
        return year.year
    else:
        return date.year


def str_to_date(_str, _form="%Y-%m-%d"):
    """Converte una stringa in datetime."""
    if _str not in [None, "None", "nan", ""] and isinstance(_str, str):
        return datetime.strptime(_str, _form)
    elif isinstance(_str, datetime) or isinstance(_str, date) and _str not in ["", None]:
        return _str
    else:
        return None


def date_to_str(_date, _form="%Y-%m-%d"):
    """Converte datetime in stringa."""
    if _date not in [None, "None", "nan", ""] and isinstance(_date, datetime) or isinstance(_date, date):
        return datetime.strftime(_date, _form)
    elif isinstance(_date, str) and date not in ["", None]:
        return _date
    else:
        return None


def not_empty(_v):
    """Verifica se il dato passato è vuoto o da non considerare."""
    if _v in ["", "-", None]:
        return None
    else:
        _v = _v.strip()
        return _v


def status_true_false(_stat):
    """Cambia valori SI, NO in True, False."""
    if _stat == "NO":
        return False
    else:
        return True


def status_si_no(_str):
    """Verifica se il dato passato contiene True o False e li converte in SI o NO."""
    if _str in ["SI", "si", "NO", "no"]:
        return _str
    elif _str is True:
        return "SI"
    else:
        return "NO"
