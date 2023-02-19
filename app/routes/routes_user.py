import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, url_for, request
from sqlalchemy.exc import IntegrityError

from app.app import db, session
from app.forms.form_account import FormAccountUpdate, FormUserSignup
from app.forms.forms import FormPswReset
from app.models.accounts import User
from app.utilitys.functions import token_admin_validate
from app.utilitys.functions_accounts import psw_hash

VIEW = "/user/view/"
VIEW_FOR = "user_view"
VIEW_HTML = "user/user_view.html"

CREATE = "/user/create/"
CREATE_FOR = "user_create"
CREATE_HTML = "user/user_create.html"

HISTORY = "/user/view/history/<int:_id>"
HISTORY_FOR = "user_view_history"
HISTORY_HTML = "user/user_view_history.html"

UPDATE = "/user/update/<int:_id>"
UPDATE_FOR = "user_update"
UPDATE_HTML = "user/user_update.html"

RESET_PSW = "/user/reset_password/<int:_id>"
RESET_PSW_FOR = "user_reset_password"
RESET_PSW_HTML = "user/user_reset_password.html"


@app.route(VIEW, methods=["GET", "POST"])
@token_admin_validate
def user_view():
	"""Visualizzo informazioni User."""
	# Estraggo la lista degli utenti amministratori
	_list = User.query.all()
	_list = [r.to_dict() for r in _list]

	db.session.close()
	return render_template(VIEW_HTML, form=_list, create=CREATE_FOR, update=UPDATE_FOR, history=HISTORY_FOR)


@app.route(CREATE, methods=["GET", "POST"])
@token_admin_validate
def user_create():
	"""Creazione Utente Consorzio."""
	form = FormUserSignup()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		new_user = User(
			username=form_data["username"].replace(" ", ""),
			name=form_data["name"].strip(),
			last_name=form_data["last_name"].strip(),
			email=form_data["email"].strip(),
			phone=form_data["phone"].strip(),
			password=psw_hash(form_data["new_password_1"].replace(" ", "")),
			psw_changed=form_data["psw_changed"],
			note=form_data["note"].strip()
		)
		try:
			User.create(new_user)
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
	from app.routes.routes_buyer import HISTORY_FOR as BUYER_HISTORY
	from app.routes.routes_event import HISTORY_FOR as EVENT_HISTORY

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
	return render_template(
		HISTORY_HTML, form=_user, view=VIEW_FOR, update=UPDATE_FOR, reset_psw=RESET_PSW_FOR,
		history_list=history_list, h_len=len(history_list), event_history=EVENT_HISTORY,
		buyer_list=buyer_list, b_len=len(buyer_list), buyer_history=BUYER_HISTORY
	)


@app.route(UPDATE, methods=["GET", "POST"])
@token_admin_validate
def user_update(_id):
	"""Aggiorna dati Utente."""
	from app.routes.routes_event import event_create

	# recupero i dati
	user = User.query.get(_id)
	form = FormAccountUpdate(obj=user)

	if form.validate_on_submit():
		new_data = FormAccountUpdate(request.form).to_dict()
		# print("NEW_DATA:", json.dumps(new_data, indent=2))

		previous_data = user.to_dict()
		previous_data.pop("updated_at")

		try:
			User.update(_id, new_data)
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
		_event = event_create(_event, user_id=_id)
		return redirect(url_for(HISTORY_FOR, _id=_id))
	else:
		_info = {
			'created_at': user.created_at,
			'updated_at': user.updated_at,
		}
		db.session.close()
		return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)


@app.route(RESET_PSW, methods=["GET", "POST"])
def user_reset_password(_id):
	"""Resetta password Utente Servizio dalla console di amministrazione."""
	from app.routes.routes_event import event_create

	form = FormPswReset()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		new_password = psw_hash(form_data["new_password_1"].replace(" ", "").strip())

		_user = User.query.get(_id)
		# print(f"UTENTE {_user.username}.")

		if new_password == _user.password:
			session.clear()
			db.session.close()
			flash("La nuova password inserita è uguale a quella registrata.")
			return render_template(RESET_PSW_HTML, form=form, id=_id, history=HISTORY_FOR)
		else:
			try:
				_user.password = new_password
				_user.psw_changed = False
				_user.updated_at = datetime.now()
				# print(f"PASSWORD utente {_user.username}.")

				User.update(_id, _user)
				flash(f"PASSWORD utente {_user.username} resettata correttamente!")
				flash(f"Comunica all'utente la nuova password e che dovrà cambiarla dopo essersi registrato al portale.")

				_event = {
					"executor": session["username"],
					"Modification": f"Password reset for user: {_user.username}"
				}
				_event = event_create(_event, user_id=_id)
				return redirect(url_for(HISTORY_FOR, _id=_id))
			except Exception as err:
				flash(f'ERRORE: {err}')
				return render_template(RESET_PSW_HTML, form=form, id=_id, history=HISTORY_FOR)
	else:
		return render_template(RESET_PSW_HTML, form=form, id=_id, history=HISTORY_FOR)
