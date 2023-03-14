import json
from datetime import datetime
from uuid import uuid4

from flask import current_app as app, flash, redirect, render_template, url_for, request, jsonify, make_response

from app.app import session, db
from app.forms.forms import FormLogin
from app.models.accounts import Administrator
from app.models.auth_tokens import AuthToken
from app.utilitys.functions import buyer_log_in, token_buyer_validate
from app.utilitys.functions_accounts import psw_hash, __save_auth_token


@app.route("/", methods=["GET", "POST"])
def login():
	"""Effettua la log-in."""
	form = FormLogin()
	if form.validate_on_submit():
		_admin = Administrator.query.filter_by(
			username=form.username.data, password=psw_hash(str(form.password.data))
		).first()
		# print("ACCOUNT:", json.dumps(_admin.to_dict(), indent=2))

		if _admin:
			_tokens = _admin.auth_tokens.all()
			if _tokens:
				count = len(_tokens)
				token = None
				for t in _tokens:
					if t.expires_at > datetime.now():
						token = t.token
					else:
						count -= 1
						AuthToken.remove(t)
				
				if count == 0 and token is None:
					token = uuid4()
					_auth_token = __save_auth_token(token, _admin.id)
			else:
				token = str(uuid4())
				_auth_token = __save_auth_token(token, _admin.id)

			session.permanent = False
			session["token_login"] = str(token)
			session["username"] = _admin.username
			session["user"] = _admin.to_dict()

			db.session.close()
			if _admin.psw_changed is True:
				print("LOG-IN: OK")
				return redirect(url_for('farmer_view'))
			else:
				print("LOG-IN: OK")
				flash('Devi cambiare la password che ti è stata assegnata.')
				return redirect(url_for('admin_update_password', _id=_admin.id))
		else:
			print("LOG-IN: KO")
			flash("Invalid username or password. Please try again!", category="alert")
			return render_template("login.html", form=form)
	else:
		print("LOG-IN...")
		return render_template("login.html", form=form)


@app.route("/buyer/login/<cert_nr>", methods=["GET", "POST"])
def login_buyer(cert_nr):
	"""Effettua la log-in."""
	form = FormLogin()
	if form.validate_on_submit():
		# print(f"USER: {form.username.data}")
		data = buyer_log_in(form)
		if data:
			session.permanent = False
			session['cert_nr'] = cert_nr
			session["token_login"] = str(data["token"])
			session["username"] = data["username"]
			session['user'] = data
			return redirect(url_for('cookie_consent', cert_nr=cert_nr))
		else:
			flash("Invalid username or password. Please try again!", category="alert")
			return render_template("buyer/buyer_login.html", form=form, cert_nr=cert_nr)
	else:
		return render_template("buyer/buyer_login.html", form=form, cert_nr=cert_nr)


@app.route("/logout/")
def logout(msg=None):
	"""Effettua il log-out ed elimina i dati della sessione."""
	session.clear()
	if msg:
		flash(msg)
	flash("Log-Out effettuato.")
	return redirect(url_for('login'))


@app.route("/logout/buyer/<cert_nr>/")
def logout_buyer(cert_nr):
	"""Effettua il log-out ed elimina i dati della sessione."""
	session.clear()
	flash("Log-Out effettuato.")
	return redirect(url_for('login_buyer', cert_nr=cert_nr))


@app.route("/cookie_consent/<cert_nr>/", methods=["GET", "POST"])
@token_buyer_validate
def cookie_consent(cert_nr):
	if request.method == "POST":
		response = make_response(render_template("cookie_consent.html"))
		response.set_cookie("functional_cookies_consent", "accepted")

		if session['user']['psw_changed'] is True:
			if cert_nr not in ["", "None", None]:
				return redirect(url_for('cert_cons_buyer_view_history', cert_nr=cert_nr))
			else:
				return redirect(url_for('cert_cons_buyer_view'))
		else:
			flash('Devi cambiare la password che ti è stata assegnata.')
			return redirect(url_for('buyer_reset_password', _id=session['user']['id']))
	else:
		functional_cookies_consent = request.cookies.get("functional_cookies_consent")
		if functional_cookies_consent == "accepted":
			if session['user']['psw_changed'] is True:
				if cert_nr not in ["", "None", None]:
					return redirect(url_for('cert_cons_buyer_view_history', cert_nr=cert_nr))
				else:
					return redirect(url_for('cert_cons_buyer_view'))
			else:
				flash('Devi cambiare la password che ti è stata assegnata.')
				return redirect(url_for('buyer_reset_password', _id=session['user']['id']))
		else:
			return render_template("cookie_consent.html", cert_nr=cert_nr)


@app.route("/privacy_policy/<cert_nr>/", methods=["GET", "POST"])
@token_buyer_validate
def privacy_policy(cert_nr):
	return render_template("privacy_policy.html", cert_nr=cert_nr)


@app.route('/cache-me')
def cache():
	return "nginx will cache this response"


@app.route('/info')
def info():
	resp = {
		'connecting_ip': request.headers['X-Real-IP'],
		'proxy_ip': request.headers['X-Forwarded-For'],
		'host': request.headers['Host'],
		'user-agent': request.headers['User-Agent']
	}
	return jsonify(resp)


@app.route('/flask-health-check')
def flask_health_check():
	return "success"


@app.route("/map")
def map():  # noqa
	return render_template("map.html")
