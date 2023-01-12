import base64
import json
from datetime import datetime

import requests
import sqlalchemy
from flask import jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from app.models.tokens import AuthToken
from app.var_ambient import variables as var
from app.app import db

disable_warnings(InsecureRequestWarning)


def validate_token_user(_token):
    """Valido il token ricevuto."""
    authenticated = AuthToken.query.filter_by(token=_token).first()
    if authenticated in ["", None] or authenticated.expires_at < datetime.now() or authenticated.user_id in ["", None]:
        flash("You don't have a valid authentication token, please log in.")
        return False
    else:
        return True


def validate_token_admin(_token):
    """Valido il token ricevuto."""
    authenticated = AuthToken.query.filter_by(token=_token).first()
    # print(authenticated.admin_id, authenticated.user_id, authenticated.expires_at, authenticated.token)
    if authenticated in ["", None]:
        flash(f"There is no authenticated log in for your username. Please log in again with an administrator account.")
        return False
    elif authenticated.expires_at < datetime.now():
        flash("Your authenticated log in is expired. Please log in again with an administrator account.")
        return False
    elif authenticated.admin_id in ["", None]:
        flash(f"Your account {authenticated.admin_id} does not allow this operation. "
              f"Please log in with an administrator account.")
        return False
    else:
        return True


def admin_log_in(form):
    """API - Login e ottengo il token."""
    url = var.apiUrls_admin["admin_login"]
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
