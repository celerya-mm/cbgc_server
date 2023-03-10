import json
from datetime import datetime, date
from functools import wraps

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from flask import url_for, redirect
from jinja2.utils import htmlsafe_json_dumps
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from app.app import session
from app.models.auth_tokens import AuthToken
from app.var_ambient import variables as var

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


def token_buyer_validate(func):
	"""Eseguo la funzione solo se presente token autenticazione user valido."""

	@wraps(func)
	def wrap(*args, **kwargs):
		if "token_login" in session.keys():
			# controlla validità token
			authenticated = AuthToken.query.filter_by(token=session["token_login"]).first()
			if authenticated is None:
				print("AUTHORIZATION_CHECK_FAIL_2")
				return redirect(url_for('logout_buyer', cert_nr=session["cert_nr"]))
			elif authenticated.expires_at < datetime.now():
				print("AUTHORIZATION_CHECK_FAIL_3")
				return redirect(url_for('logout_buyer', cert_nr=session["cert_nr"]))
			elif authenticated.user_id in ["", None]:
				print("AUTHORIZATION_CHECK_FAIL_4")
				return redirect(url_for('logout_buyer', cert_nr=session["cert_nr"]))
			else:
				print("AUTHORIZATION_CHECK_PASS")
				# esegue la funzione
				return func(*args, **kwargs)
		else:
			print("AUTHORIZATION_CHECK_FAIL_1")
			return redirect(url_for('logout_buyer', cert_nr=session["cert_nr"]))

	return wrap


def token_admin_validate(func):
	"""Eseguo la funzione solo se presente token autenticazione admin valido."""

	@wraps(func)
	def wrap(*args, **kwargs):
		if session is not None and "token_login" in session.keys():
			# controlla validità token
			authenticated = AuthToken.query.filter_by(token=session["token_login"]).first()
			if authenticated is None:
				print("AUTHORIZATION_CHECK_FAIL: no valid token.")
				msg = f"Non è stato passato un token valido, ripetere la login."
				return redirect(url_for('logout', msg=msg))
			elif authenticated.expires_at < datetime.now():
				print("AUTHORIZATION_CHECK_FAIL: token is expired.")
				msg = f"Il token è scaduto: {authenticated.expires_at}, ripetere la login."
				return redirect(url_for('logout', msg=msg))
			elif authenticated.admin_id in ["", None]:
				print("AUTHORIZATION_CHECK_FAIL: no user_admin returned.")
				msg = f"Non è stato registrato nessun utente, effettuare la login."
				return redirect(url_for('logout', msg=msg))
			else:
				print("AUTHORIZATION_CHECK_PASS")
				# esegue la funzione
				return func(*args, **kwargs)
		else:
			print("AUTHORIZATION_CHECK_FAIL: no token passed.")
			msg = f'Per accedere devi prima effettuare la login.'
			return redirect(url_for('logout', msg=msg))

	return wrap


def admin_log_in(form):
	"""API - Login e ottengo il token."""
	url = var.apiUrls_admin["admin_login"]
	payload = json.dumps({"username": form.username.data, "password": form.password.data})
	headers = {'Content-Type': 'application/json'}
	response = requests.request("POST", url, headers=headers, data=payload, verify=False)
	try:
		# print("RESPONSE:", response.text)
		_resp = json.loads(response.text)
		return _resp["data"]
	except Exception as err:
		print(f"ERRORE_RISPOSTA_SERVER: {err}")
		return False


def buyer_log_in(form):
	"""API - Login e ottengo il token."""
	url = var.apiUrls_buyer["buyer_login"]
	payload = json.dumps({"username": form.username.data, "password": form.password.data})
	headers = {'Content-Type': 'application/json'}
	response = requests.request("POST", url, headers=headers, data=payload, verify=False)
	try:
		# print("RESPONSE:", response.text)
		_resp = json.loads(response.text)
		return _resp["data"]
	except Exception as err:
		print(f"ERRORE_RISPOSTA_SERVER: {err}")
		return False


def address_mount(address, cap, city):
	"""Monta indirizzo completo."""
	if address and cap and city:
		full_address = f"{address.strip().replace('  ', ' ')} - {cap.strip()} - {city.strip().replace('  ', ' ')}"
	elif address and cap:
		full_address = f"{address.strip().replace('  ', ' ')} - {cap.strip()}"
	elif address and city:
		full_address = f"{address.strip().replace('  ', ' ')} - {city.strip().replace('  ', ' ')}"
	elif cap and city:
		full_address = f"{cap.strip()} - {city.strip().replace('  ', ' ')}"
	elif address:
		full_address = address.strip().replace('  ', ' ')
	elif city:
		full_address = city.strip().replace('  ', ' ')
	elif cap:
		full_address = cap.strip()
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
	if date in ["", None]:
		return None
	elif isinstance(date, str):
		year = datetime.strptime(date, "%Y-%m-%d")
		return year.year
	else:
		return date.year


def str_to_date(_str, _form="%Y-%m-%d"):
	"""Converte una stringa in datetime."""
	if _str in [None, ""]:
		return None
	elif _str not in [None, "None", "nan", ""] and isinstance(_str, str):
		return datetime.strptime(_str, _form)
	else:
		return _str


def date_to_str(_date, _form="%Y-%m-%d"):
	"""Converte datetime in stringa."""
	if _date in [None, "None", "nan", ""]:
		return None
	elif isinstance(_date, date):
		return date.strftime(_date, "%Y-%m-%d")
	elif isinstance(_date, datetime):
		return datetime.strftime(_date, _form)
	else:
		return _date


def not_empty(_v):
	"""Verifica se il dato passato è vuoto o da non considerare."""
	if _v in ["", "-", None, 0]:
		return None
	else:
		return _v


def status_true_false(_stat):
	"""Cambia valori SI, NO in True, False."""
	if _stat == "NO" or _stat is False:
		return False
	else:
		return True


def status_si_no(_str):
	"""Verifica se il dato passato contiene True o False e li converte in SI o NO."""
	if _str in ["SI", True]:
		return "SI"
	else:
		return "NO"


def calc_age(birth, slaught):  # noqa
	"""Calcola la differenza in mesi tra due date."""
	if isinstance(birth, str):
		birth = datetime.strptime(birth, '%Y-%m-%d')
	if isinstance(slaught, str):
		slaught = datetime.strptime(slaught, '%Y-%m-%d')  # noqa

	# print("BIRTH:", birth, "SLAUGHT:", slaught)
	difference = relativedelta(slaught, birth)
	if difference.years > 0:
		months = difference.years * 12
		months = difference.months + months
	else:
		months = difference.months
	# print("MESI:", months)
	return months


def dict_group_by(_dict, group_d, group_f=None, year=False):  # group_d deve essere l'anno se year=True
	"""Raggruppa un DF per la richiesta passata (group)."""
	# crea DF
	df = pd.DataFrame.from_records(_dict)
	if year:
		# filtra DF al massimo cinque anni indietro
		current_year = datetime.now().year
		past_year = current_year - 5
		df = df.loc[df[group_d] >= past_year]

	if group_f:  #
		# raggruppa il DF
		df = df.groupby([group_d, group_f]).size().reset_index()
		df.rename(columns={0: 'number'}, inplace=True)
		dct = df.to_dict("records")
	else:
		# raggruppa il DF
		df = df.groupby(by=group_d).size().reset_index()
		df.rename(columns={0: 'number'}, inplace=True)
		dct = df.to_dict("records")
	return dct


def serialize_dict(obj):
	"""Verifica presenza campi data e li converte in iso format."""
	if isinstance(obj, datetime):
		return obj.isoformat()
	elif isinstance(obj, date):
		return obj.isoformat()
	else:
		raise TypeError(f"{obj} is not JSON serializable")
