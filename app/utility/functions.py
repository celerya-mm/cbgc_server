import base64
import json
import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from flask import flash, redirect, session, url_for
from app.var_ambient import variables as var

disable_warnings(InsecureRequestWarning)


def admin_log_in(form):
    """API - Login e ottengo il token."""
    url = var.apiUrls["admin_login"]
    payload = json.dumps({"username": form.username.data, "password": form.password.data})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    print("RESPONSE:", response.text)
    dati = json.loads(response.text)
    try:
        # dati = json.loads(response.text)
        token = dati["token"]
        token = base64.b64encode(bytes(token, "utf-8"))
        return token
    except Exception as err:
        print(f"ERRORE_RISPOSTA_SERVER: {err}")
        return False


def user_log_in(form):
    """API - Login e ottengo il token."""
    url = var.apiUrls["user_login"]
    payload = json.dumps({"username": form.username.data, "password": form.password.data})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    print("RESPONSE:", response.text)
    dati = json.loads(response.text)
    try:
        # dati = json.loads(response.text)
        token = dati["token"]
        token = base64.b64encode(bytes(token, "utf-8"))
        return token
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
