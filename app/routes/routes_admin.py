import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db, session
from ..forms.form_account import FormAccountUpdate, FormAdminSignup
from ..forms.forms import FormPswChange
from ..models.accounts import Administrator
from ..utilitys.functions import event_create, token_admin_validate, not_empty
from ..utilitys.functions_accounts import psw_hash

VIEW = "/admin/view/"
VIEW_FOR = "admin_view"
VIEW_HTML = "admin/admin_view.html"

CREATE = "/admin/create/"
CREATE_FOR = "admin_create"
CREATE_HTML = "admin/admin_create.html"

HISTORY = "/admin/view/history/<_id>"
HISTORY_FOR = "admin_view_history"
HISTORY_HTML = "admin/admin_view_history.html"

UPDATE = "/admin/update/<_id>"
UPDATE_FOR = "admin_update"
UPDATE_HTML = "admin/admin_update.html"

UPDATE_PSW = "/admin/update/psw/<_id>"
UPDATE_PSW_FOR = "admin_update_password"
UPDATE_PSW_HTML = "admin/admin_update_password.html"


@app.route(VIEW, methods=["GET", "POST"])
@token_admin_validate
def admin_view():
	"""Visualizzo informazioni Utente Amministratore."""
	if "username" in session.keys():
		# Estraggo l'utente amministratore corrente
		admin = Administrator.query.filter_by(username=session["username"]).first()
		_admin = admin.to_dict()
		session["admin"] = _admin

		# Estraggo la lista degli utenti amministratori
		_list = Administrator.query.all()
		_list = [r.to_dict() for r in _list]
		return render_template(VIEW_HTML, admin=_admin, form=_list, create=CREATE_FOR, update=UPDATE_FOR,
		                       update_psw=UPDATE_PSW_FOR, history=HISTORY_FOR)
	else:
		flash(f"Token autenticazione non presente, devi eseguire la Log-In.")
		return redirect(url_for('logout'))


@app.route(CREATE, methods=["GET", "POST"])
@token_admin_validate
def admin_create():
	"""Creazione Utente Amministratore."""
	form = FormAdminSignup()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		# print("FORM_DATA", json.dumps(form_data, indent=2))

		new_admin = Administrator(
			username=form_data["username"].replace(" ", ""),
			name=form_data["name"].strip(),
			last_name=form_data["last_name"].strip(),
			email=form_data["email"].strip(),
			phone=form_data["phone"].strip(),
			password=psw_hash(form_data["new_password_1"].replace(" ", "")),
			note=form_data["note"].strip(),
		)
		try:
			db.session.add(new_admin)
			db.session.commit()
			flash("Utente amministratore creato correttamente.")
			return redirect(url_for(VIEW_FOR))
		except IntegrityError as err:
			db.session.rollback()
			flash(f"ERRORE: {str(err.orig)}")
			return render_template(CREATE_HTML, form=form, view=VIEW_FOR)
	else:
		return render_template(CREATE_HTML, form=form, view=VIEW_FOR)


@app.route(HISTORY, methods=["GET", "POST"])
@token_admin_validate
def admin_view_history(_id):
	"""Visualizzo la storia delle modifiche al record utente Administrator."""
	print("ID:", _id)
	from ..routes.routes_event import HISTORY_FOR as EVENT_HISTORY
	# Estraggo l'ID dell'utente amministratore corrente
	session["id_admin"] = _id

	# Interrogo il DB
	admin = Administrator.query.get(_id)
	_admin = admin.to_dict()

	# Estraggo la storia delle modifiche per l'utente
	history_list = admin.events
	history_list = [history.to_dict() for history in history_list]
	len_history = len(history_list)
	db.session.close()

	return render_template(HISTORY_HTML, form=_admin, history_list=history_list, h_len=len_history, view=VIEW_FOR,
	                       update=UPDATE_FOR, update_psw=UPDATE_PSW_FOR, event_history=EVENT_HISTORY)


@app.route(UPDATE, methods=["GET", "POST"])
@token_admin_validate
def admin_update(_id):
	"""Aggiorna Utente Amministratore."""
	form = FormAccountUpdate()
	if form.validate_on_submit():
		new_data = json.loads(json.dumps(request.form))
		new_data.pop('csrf_token', None)
		# print("FORM_DATA_PASS:", json.dumps(new_data, indent=2))

		administrator = Administrator.query.get(_id)
		db.session.close()
		previous_data = administrator.to_dict()
		# print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

		new_data["full_name"] = f'{new_data["name"]} {new_data["last_name"]}'
		new_data["created_at"] = administrator.created_at
		new_data["updated_at"] = datetime.now()

		new_data["note"] = not_empty(new_data["note"])

		print("NEW_DATA:", new_data)
		try:
			db.session.query(Administrator).filter_by(id=_id).update(new_data)
			db.session.commit()
			db.session.close()
			flash("UTENTE aggiornato correttamente.")
		except IntegrityError as err:
			db.session.rollback()
			flash(f"ERRORE: {str(err.orig)}")
			_info = {
				'created_at': administrator.created_at,
				'updated_at': administrator.updated_at,
			}
			return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)

		_event = {
			"username": session["username"],
			"table": Administrator.__tablename__,
			"Modification": f"Update account Administrator whit id: {_id}",
			"Previous_data": previous_data
		}
		if event_create(_event, admin_id=_id):
			return redirect(url_for(HISTORY_FOR, _id=_id))
		else:
			flash("ERRORE creazione evento. Ma il record è stato modificato correttamente.")
			return redirect(url_for(HISTORY_FOR, _id=_id))

	else:
		# recupero i dati
		admin = Administrator.query.get(_id)
		db.session.close()
		# print("ADMIN:", admin)
		# print("ADMIN_FIND:", json.dumps(admin.to_dict(), indent=2))

		form.username.data = admin.username
		form.name.data = admin.name
		form.last_name.data = admin.last_name
		form.email.data = admin.email
		form.phone.data = admin.phone
		form.note.data = admin.note

		_info = {
			'created_at': admin.created_at,
			'updated_at': admin.updated_at,
		}
		# print("ADMIN_UPDATE:", json.dumps(form.to_dict(form), indent=2))
		return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)


@app.route(UPDATE_PSW, methods=["GET", "POST"])
@token_admin_validate
def admin_update_password(_id):
	"""Aggiorna password Utente Amministratore."""
	form = FormPswChange()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		_admin = json.loads(json.dumps(session["admin"]))

		old_password = psw_hash(form_data["old_password"].replace(" ", "").strip())
		# print("OLD:", old_password)
		new_password = psw_hash(form_data["new_password_1"].replace(" ", "").strip())
		# print("NEW:", new_password)

		administrator = Administrator.query.get(_id)
		db.session.close()

		if new_password == administrator.password:
			flash("The 'New Password' inserted is equal to 'Registered Password'.")
			return render_template("admin/admin_update_password.html", form=form, id=_id)
		elif old_password != administrator.password:
			flash("The 'Current Passwort' inserted does not match the 'Registered Password'.")
			return render_template(UPDATE_PSW_HTML, form=form, id=_id, history=HISTORY_FOR)
		else:
			administrator.password = new_password
			administrator.updated_at = datetime.now()

			db.session.commit()
			db.session.close()
			flash("PASSWORD aggiornata correttamente! Effettua una nuova Log-In.")
			_event = {
				"username": session["username"],
				"Modification": "Password changed"
			}
			if event_create(_event, admin_id=_id):
				return redirect(url_for('logout'))
			else:
				flash("ERRORE creazione evento DB. Ma la password è stata modificata correttamente.")
				return redirect(url_for('logout'))
	else:
		return render_template(UPDATE_PSW_HTML, form=form, id=_id, history=HISTORY_FOR)
