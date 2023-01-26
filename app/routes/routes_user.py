import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db, session
from ..forms.form_account import FormAccountUpdate, FormUserSignup
from ..models.accounts import User
from ..utilitys.functions import event_create, token_admin_validate
from ..utilitys.functions_accounts import psw_hash

VIEW = "/user/view/"
VIEW_FOR = "user_view"
VIEW_HTML = "user/user_view.html"

CREATE = "/user/create/"
CREATE_FOR = "user_create"
CREATE_HTML = "user/user_create.html"

HISTORY = "/user/view/history/<_id>"
HISTORY_FOR = "user_view_history"
HISTORY_HTML = "user/user_view_history.html"

UPDATE = "/user/update/<_id>"
UPDATE_FOR = "user_update"
UPDATE_HTML = "user/user_update.html"


@app.route(VIEW, methods=["GET", "POST"])
@token_admin_validate
def user_view():
	"""Visualizzo informazioni User."""
	# Estraggo la lista degli utenti amministratori
	_list = User.query.all()
	db.session.close()
	_list = [r.to_dict() for r in _list]
	return render_template(VIEW_HTML, form=_list, create=CREATE_FOR, update=UPDATE_FOR, history=HISTORY_FOR)


@app.route(CREATE, methods=["GET", "POST"])
@token_admin_validate
def user_create():
	"""Creazione Utente Consorzio."""
	form = FormUserSignup()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		# print("USER_FORM_DATA", json.dumps(form_data, indent=2))

		new_user = User(
			username=form_data["username"].replace(" ", ""),
			name=form_data["name"].strip(),
			last_name=form_data["last_name"].strip(),
			email=form_data["email"].strip(),
			phone=form_data["phone"].strip(),
			password=psw_hash(form_data["new_password_1"].replace(" ", "")),
			note=form_data["note"].strip()
		)
		try:
			db.session.add(new_user)
			db.session.commit()
			db.session.close()
			flash("UTENTE servizio creato correttamente.")
			return redirect(url_for(VIEW_FOR))
		except IntegrityError as err:
			db.session.rollback()
			db.session.close()
			flash(f"ERRORE: {str(err.orig)}")
			return render_template(CREATE_HTML, form=form, view=VIEW_FOR)
	else:
		return render_template(CREATE_HTML, form=form, view=VIEW_FOR)


@app.route(HISTORY, methods=["GET", "POST"])
@token_admin_validate
def user_view_history(_id):
	"""Visualizzo la storia delle modifiche al record utente Administrator."""
	from ..routes.routes_buyer import HISTORY_FOR as BUYER_HISTORY
	from ..routes.routes_event import HISTORY_FOR as EVENT_HISTORY

	# Estraggo l' ID dell'utente corrente
	session["id_user"] = _id

	# Interrogo il DB
	user = User.query.get(_id)
	_user = user.to_dict()

	# Estraggo la storia delle modifiche per l'utente
	history_list = user.events
	if history_list:
		history_list = [history.to_dict() for history in history_list]
	else:
		history_list = []

	# Estraggo la lista degli Acquirenti sotto l'utente
	buyer_list = user.buyers
	if buyer_list:
		buyer_list = [buyer.to_dict() for buyer in buyer_list]
	else:
		buyer_list = []

	db.session.close()

	return render_template(HISTORY_HTML, form=_user, view=VIEW_FOR, update=UPDATE_FOR,
	                       history_list=history_list, h_len=len(history_list), event_history=EVENT_HISTORY,
	                       buyer_list=buyer_list, b_len=len(buyer_list), buyer_history=BUYER_HISTORY)


@app.route(UPDATE, methods=["GET", "POST"])
@token_admin_validate
def user_update(_id):
	"""Aggiorna dati Utente."""
	form = FormAccountUpdate()
	if form.validate_on_submit():
		new_data = json.loads(json.dumps(request.form))
		new_data.pop('csrf_token', None)
		# print("USER_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

		user = User.query.get(_id)
		previous_data = user.to_dict()
		# print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

		new_data["full_name"] = f'{new_data["name"]} {new_data["last_name"]}'

		new_data["created_at"] = user.created_at
		new_data["updated_at"] = datetime.now()
		print("NEW_DATA:", new_data)
		try:
			db.session.query(User).filter_by(id=_id).update(new_data)
			db.session.commit()
			db.session.close()
			flash("UTENTE aggiornato correttamente.")
		except IntegrityError as err:
			db.session.rollback()
			db.session.close()
			flash(f"ERRORE: {str(err.orig)}")
			_info = {
				'created_at': user.created_at,
				'updated_at': user.updated_at,
			}
			return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)

		_event = {
			"username": session["username"],
			"table": User.__tablename__,
			"Modification": f"Update account USER whit id: {_id}",
			"Previous_data": previous_data
		}
		# print("EVENT:", json.dumps(_event, indent=2))
		if event_create(_event, user_id=_id):
			return redirect(url_for(HISTORY_FOR, _id=_id))
		else:
			flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
			return redirect(url_for(HISTORY_FOR, _id=_id))
	else:
		# recupero i dati
		user = User.query.get(_id)
		db.session.close()
		# print("USER:", user)
		# print("USER_FIND:", json.dumps(user.to_dict(), indent=2))

		form.username.data = user.username
		form.name.data = user.name
		form.last_name.data = user.last_name
		form.email.data = user.email
		form.phone.data = user.phone
		form.note.data = user.note

		_info = {
			'created_at': user.created_at,
			'updated_at': user.updated_at,
		}
		# print("USER_UPDATE:", json.dumps(form.to_dict(form), indent=2))
		return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)
