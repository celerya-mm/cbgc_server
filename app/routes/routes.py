from flask import current_app as app, flash, redirect, render_template, url_for, request, jsonify

from ..app import session

from ..forms.forms import FormLogin
from ..utilitys.functions import admin_log_in, buyer_log_in


@app.route("/", methods=["GET", "POST"])
def login():
	"""Effettua la log-in."""
	form = FormLogin()
	if form.validate_on_submit():
		# print(f"USER: {form.username.data}")
		token = admin_log_in(form)
		if token:
			session["token_login"] = token
			session["username"] = form.username.data
			return redirect(url_for('cert_cons_view'))
		else:
			flash("Invalid username or password. Please try again!", category="alert")
			return render_template("login.html", form=form)
	else:
		return render_template("login.html", form=form)


@app.route("/buyer/login/<cert_nr>", methods=["GET", "POST"])
def login_buyer(cert_nr):
	"""Effettua la log-in."""
	form = FormLogin()
	if form.validate_on_submit():
		# print(f"USER: {form.username.data}")
		data = buyer_log_in(form)
		if data:
			session['cert_nr'] = cert_nr
			session["token_login"] = data["token"]
			session["username"] = form.username.data
			if cert_nr not in ["", "None", None]:
				return redirect(url_for('cert_cons_buyer_view_history', cert_nr=cert_nr))
			else:
				return redirect(url_for('cert_cons_buyer_view'))
		else:
			flash("Invalid username or password. Please try again!", category="alert")
			return render_template("buyer/buyer_login.html", form=form, cert_nr=cert_nr)
	else:
		return render_template("buyer/buyer_login.html", form=form, cert_nr=cert_nr)


@app.route("/logout/")
def logout():
	"""Effettua il log-out ed elimina i dati della sessione."""
	session.clear()
	flash("Log-Out effettuato.")
	return redirect(url_for('login'))


@app.route("/logout/buyer/<cert_nr>/")
def logout_buyer(cert_nr):
	"""Effettua il log-out ed elimina i dati della sessione."""
	session.clear()
	flash("Log-Out effettuato.")
	return redirect(url_for('login_buyer', cert_nr=cert_nr))


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
