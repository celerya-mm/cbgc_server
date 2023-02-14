import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db, session, Message, mail, Config
from ..forms.form_account import FormAccountUpdate, FormUserSignup
from ..forms.forms import FormPswReset
from ..models.accounts import User
from ..models.tokens import calc_exp_token_reset_psw, AuthToken
from ..utilitys.functions import token_admin_validate, not_empty
from ..utilitys.functions_accounts import psw_hash, __generate_auth_token

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
	return render_template(
		HISTORY_HTML, form=_user, view=VIEW_FOR, update=UPDATE_FOR, reset_psw=RESET_PSW_FOR,
		history_list=history_list, h_len=len(history_list), event_history=EVENT_HISTORY,
		buyer_list=buyer_list, b_len=len(buyer_list), buyer_history=BUYER_HISTORY
	)


@app.route(UPDATE, methods=["GET", "POST"])
@token_admin_validate
def user_update(_id):
	"""Aggiorna dati Utente."""
	from ..routes.routes_event import event_create

	form = FormAccountUpdate()
	# recupero i dati
	user = User.query.get(_id)

	if form.validate_on_submit():
		new_data = json.loads(json.dumps(request.form))

		previous_data = user.to_dict()
		previous_data.pop("updated_at")

		user.username = new_data["username"].strip().replace(" ", "")
		user.name = new_data["name"].strip()
		user.last_name = new_data["last_name"].strip()
		user.full_name = f'{new_data["name"]} {new_data["last_name"]}'

		user.email = new_data["email"].strip().replace(" ", "")
		user.phone = new_data["phone"].strip()

		user.note = not_empty(new_data["note"].strip().replace("  ", ""))
		user.updated_at = datetime.now()
		try:
			User.update()
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
		db.session.close()
		return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)


@app.route(RESET_PSW, methods=["GET", "POST"])
def user_reset_password(_id):
	"""Aggiorna password Utente Servizio."""
	from ..routes.routes_event import event_create

	form = FormPswReset()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		new_password = psw_hash(form_data["new_password_1"].replace(" ", "").strip())

		_user = User.query.get(_id)
		print(f"UTENTE {_user.username}.")

		if new_password == _user.password:
			session.clear()
			db.session.close()
			flash("The 'New Password' inserted is equal to 'Registered Password'.")
			return render_template(RESET_PSW_HTML, form=form, id=_id, history=HISTORY_FOR)
		else:
			try:
				_user.password = new_password
				_user.updated_at = datetime.now()
				print(f"PASSWORD utente {_user.username}.")

				User.update()
				flash(f"PASSWORD utente {_user.username} resettata correttamente!")

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


@app.route('/reset_psw_user/<_id>/')
def reset_psw_user(_id):
	# estraggo dati utente
	_user = User.query.get(_id)
	_mail = _user.email

	# creo un token con validità 15 min
	_token = __generate_auth_token()

	auth_token = AuthToken(
		user_id=_id,
		token=_token,
		expires_at=calc_exp_token_reset_psw()
	)

	AuthToken.create(auth_token)

	# imposto link
	_link = f"{Config.LINK_URL}:62233/reset_psw_user_token/{_token}/"
	_link = _link.replace("/:", ":")
	try:
		# imposto e invio la mail con il link per il reset
		msg = Message(
			'Password change request in Consorzio Bue Grasso account.',
			sender="service@celerya.com",
			recipients=[_mail]
		)
		msg.body = f"Follow this link for reset your password: \n\n{_link}\n\n" \
		           f"The link expiry in 15 min."
		mail.send(msg)
		flash("Richiesta reset password inviata correttamente.")
		return redirect(url_for(HISTORY_FOR, _id=_id))
	except Exception as err:
		flash(f"Richiesta reset password NON inviata: {err}.")
		return redirect(url_for(HISTORY_FOR, _id=_id))


@app.route('/reset_psw_user/token/<_token>/')
def reset_psw_user_token(_token):
	_token = AuthToken.query.filter_by(token=_token).first()
	db.session.close()
	if datetime.now() > _token.expires_at:
		return "Il token è scaduto ripeti la procedura di ripristino password."
	else:
		_id = _token.user_id
		return redirect(url_for(RESET_PSW_FOR, _id=_id, check=False))
