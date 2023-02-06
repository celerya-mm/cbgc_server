import json
from datetime import datetime
import re
import folium

from flask import current_app as app, flash, redirect, render_template, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db, session, Message, mail, Config
from ..forms.form_buyer import FormBuyerCreate, FormBuyerUpdate
from ..forms.form_account import FormUserResetPsw
from ..forms.forms import FormPswReset
from ..models.accounts import User
from ..models.buyers import Buyer
from ..models.heads import Head
from ..models.tokens import AuthToken, calc_exp_token_reset_psw
from ..utilitys.functions import (status_si_no, status_true_false, str_to_date, token_admin_validate, address_mount,
                                  not_empty)
from ..utilitys.functions_accounts import __generate_auth_token, psw_hash

VIEW = "/buyer/view/"
VIEW_FOR = "buyer_view"
VIEW_HTML = "buyer/buyer_view.html"

CREATE = "/buyer/create/"
CREATE_FOR = "buyer_create"
CREATE_HTML = "buyer/buyer_create.html"

HISTORY = "/buyer/view/history/<_id>"
HISTORY_FOR = "buyer_view_history"
HISTORY_HTML = "buyer/buyer_view_history.html"

UPDATE = "/buyer/update/<_id>"
UPDATE_FOR = "buyer_update"
UPDATE_HTML = "buyer/buyer_update.html"


def create_map(_list):
	"""Crea una mappa dalla base dati."""
	m = folium.Map(location=[44.92, 10.01], zoom_start=6.5, name="Mappa acquirenti Consorzio", tiles=None)
	folium.TileLayer('Stamen Terrain', control=False).add_to(m)
	feature_group_m = folium.FeatureGroup(name="Macellerie", overlay=True)
	feature_group_r = folium.FeatureGroup(name="Ristoranti", overlay=True)
	feature_group_i = folium.FeatureGroup(name="Indefiniti", overlay=True)
	for record in _list:
		if record.coordinates and len(record.coordinates) > 5:
			if record.buyer_type == "Macelleria":
				color = "red"  # rosso (macellerie)
				icon = "shop"
				feature_group = feature_group_m
			elif record.buyer_type == "Ristorante":
				color = "blue"  # blue (ristorante)
				icon = "cutlery"
				feature_group = feature_group_r
			else:
				color = "grey"  # grigio (manca il tipo)
				icon = "info-sign"
				feature_group = feature_group_i

			coordinates = record.coordinates.split(", ")
			# print("COORDINATES:", coordinates)
			lat = re.findall(r'\d+\.\d+', coordinates[0].replace("(", ""))
			# print("LAT", lat)
			lat = float(lat[0])

			long = re.findall(r'\d+\.\d+', coordinates[1].replace(")", ""))
			# print("LONG:", long)
			long = float(long[0])

			html = "<style> " \
			       "h1 {font-size: 14px; color: #2B4692} " \
			       "p {font-size: 10px; margin: 5px} " \
			       "</style>" \
			       f"<h1>{record.buyer_type}</h1>" \
			       f"<p><strong>Nome:</strong> {record.buyer_name}</p>" \
			       f"<p><strong>Indirizzo:</strong> {record.full_address}</p>" \
			       f"<p><strong>Telefono:</strong> {record.phone}</p>"

			iframe = folium.IFrame(html=html, height=450, ratio=0.2)
			popup = folium.Popup(iframe)

			tooltip = "Clicca!"

			folium.Marker(
				location=[lat, long], popup=popup, tooltip=tooltip, icon_size=(20, 20),
				icon=folium.Icon(color=color, prefix='fa', icon=icon)
			).add_to(feature_group)

	feature_group_m.add_to(m)
	feature_group_r.add_to(m)
	feature_group_i.add_to(m)

	folium.LayerControl().add_to(m)

	return m._repr_html_()  # noqa


@app.route(VIEW, methods=["GET", "POST"])
@token_admin_validate
def buyer_view():
	"""Visualizza informazioni Acquirenti."""
	# Estraggo la lista degli allevatori
	_list = Buyer.query.all()

	m = create_map(_list)
	with open("./app/templates/map.html", "wb") as f:
		f.write(m.encode('utf-8'))

	_list = [r.to_dict() for r in _list]

	db.session.close()
	return render_template(
		VIEW_HTML, form=_list, create=CREATE_FOR, update=UPDATE_FOR, history=HISTORY_FOR)


@app.route(CREATE, methods=["GET", "POST"])
@token_admin_validate
def buyer_create():
	"""Creazione Acquirente Consorzio."""
	form = FormBuyerCreate()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		# print("BUYER_FORM_DATA", json.dumps(form_data, indent=2))

		user_id = Buyer.query.filter_by(username=form_data["user_id"]).first()
		# print("USER_ID:", user_find.id)

		new_buyer = Buyer(
			buyer_name=form_data["buyer_name"].strip(),
			buyer_type=form_data["buyer_type"].strip(),
			email=form_data["email"].strip(),
			phone=form_data["phone"].strip(),
			address=form_data["address"].strip(),
			cap=form_data["cap"].strip(),
			coordinates=form_data["coordinates"].strip(),
			city=form_data["city"].strip(),
			affiliation_start_date=form_data["affiliation_start_date"],
			affiliation_status=status_true_false(form_data["affiliation_status"]),
			user_id=user_id.id,
			note=form_data["note"].strip()
		)

		try:
			db.session.add(new_buyer)
			db.session.commit()
			db.session.close()
			flash("ACQUIRENTE creato correttamente.")
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
def buyer_view_history(_id):
	"""Visualizzo la storia delle modifiche al record utente Administrator."""
	from ..routes.routes_user import HISTORY_FOR as USER_HISTORY
	from ..routes.routes_cert_cons import HISTORY_FOR as CONS_HISTORY
	from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY
	from ..routes.routes_event import HISTORY_FOR as EVENT_HISTORY

	# Interrogo il DB
	buyer = Buyer.query.get(int(_id))
	_buyer = buyer.to_dict()

	# Estraggo gli utenti collegati
	user = buyer.user_id
	if user:
		user = User.query.get(user)
		user.to_dict()

	# Estraggo la storia delle modifiche per l'acquirente
	history_list = buyer.events
	if history_list:
		history_list = [history.to_dict() for history in history_list]
	else:
		history_list = []

	# estraggo i certificati del consorzio e i capi acquistati
	cons_list = buyer.cons_certs
	head_list = []
	if cons_list:
		cons_list = [cert.to_dict() for cert in cons_list]
		for cert in cons_list:
			_h = Head.query.get(cert["head_id"])
			if _h and _h not in head_list:
				head_list.append(_h)
	# print("LEN:", len(cons_list), "DATA:", cons_list)
	else:
		cons_list = []

	db.session.close()
	return render_template(
		HISTORY_HTML, form=_buyer, update=UPDATE_FOR, view=VIEW_FOR,
		user=user, user_history=USER_HISTORY, event_history=EVENT_HISTORY,
		history_list=history_list, h_len=len(history_list),
		cons_list=cons_list, len_cons=len(cons_list), cons_history=CONS_HISTORY,
		head_list=head_list, len_heads=len(head_list), head_history=HEAD_HISTORY
	)


@app.route(UPDATE, methods=["GET", "POST"])
@token_admin_validate
def buyer_update(_id):
	"""Aggiorna dati Acquirente."""
	from ..routes.routes_event import event_create

	form = FormBuyerUpdate()
	if form.validate_on_submit():
		# recupero i dati e li converto in dict
		new_data = json.loads(json.dumps(request.form))
		new_data.pop('csrf_token', None)
		# print("BUYER_UPDATE_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

		buyer = Buyer.query.get(_id)

		previous_data = buyer.to_dict()
		previous_data.pop("updated_at")
		# print("BUYER_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

		new_data["full_address"] = address_mount(new_data["address"], new_data["cap"], new_data["city"])
		new_data["coordinates"] = new_data["coordinates"]

		new_data["affiliation_start_date"] = str_to_date(new_data["affiliation_start_date"])
		new_data["affiliation_end_date"] = str_to_date(new_data["affiliation_end_date"])
		new_data["affiliation_status"] = status_true_false(new_data["affiliation_status"])

		new_data["phone"] = not_empty(new_data["phone"])
		new_data["email"] = not_empty(new_data["email"])
		new_data["note"] = not_empty(new_data["note"])

		if new_data["user_id"] not in ["", "-", None]:
			new_data["user_id"] = int(new_data["user_id"].split(" - ")[0])
		else:
			new_data["user_id"] = None

		new_data["created_at"] = buyer.created_at
		new_data["updated_at"] = datetime.now()
		# print("NEW_DATA:", new_data)
		try:
			db.session.query(Buyer).filter_by(id=_id).update(new_data)
			db.session.commit()
			flash("ACQUIRENTE aggiornato correttamente.")
		except IntegrityError as err:
			db.session.rollback()
			db.session.close()
			flash(f"ERRORE: {str(err.orig)}")
			_info = {
				'created_at': buyer.created_at,
				'updated_at': buyer.updated_at,
			}
			return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)

		_event = {
			"username": session["username"],
			"table": Buyer.__tablename__,
			"Modification": f"Update Buyer whit id: {_id}",
			"Previous_data": previous_data
		}

		db.session.close()

		# print("BUYER_EVENT:", json.dumps(_event, indent=2))
		_event = event_create(_event, buyer_id=_id)
		if _event is True:
			return redirect(url_for(HISTORY_FOR, _id=_id))
		else:
			flash(_event)
			return redirect(url_for(HISTORY_FOR, _id=_id))
	else:
		# recupero i dati del record
		buyer = Buyer.query.get(int(_id))
		# print("BUYER_FIND:", buyer, type(buyer))

		form.buyer_name.data = buyer.buyer_name
		form.buyer_type.data = buyer.buyer_type

		form.email.data = buyer.email
		form.phone.data = buyer.phone

		form.address.data = buyer.address
		form.cap.data = buyer.cap
		form.city.data = buyer.city
		form.coordinates.data = buyer.coordinates

		form.affiliation_start_date.data = str_to_date(buyer.affiliation_start_date)
		form.affiliation_end_date.data = str_to_date(buyer.affiliation_end_date)
		form.affiliation_status.data = status_si_no(buyer.affiliation_status)

		form.note.data = buyer.note

		_info = {
			'created_at': buyer.created_at,
			'updated_at': buyer.updated_at,
		}
		# print("BUYER_:", form)
		# print("BUYER_FORM:", json.dumps(form.to_dict(form), indent=2))
		db.session.close()
		return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)


@app.route('/buyer/email_reset_psw/<cert_nr>/', methods=["GET", "POST"])
def buyer_email_reset_psw(cert_nr):
	form = FormUserResetPsw()
	if form.validate_on_submit():
		print("EMAIL:", form.email.data)
		try:
			# estraggo dati utente
			_user = db.session.query(User).filter_by(email=str(form.email.data)).first()
		except Exception as err:
			flash(f"Nessun utente assegnato alla email inserita: {str(form.email.data)}. Errore: {err}")
			return render_template("buyer/buyer_insert_email_reset_password.html", form=form, cert_nr=cert_nr)

		# creo un token con validità 15 min
		_token = __generate_auth_token()
		auth_token = AuthToken(
			user_id=_user.id,
			token=_token,
			expires_at=calc_exp_token_reset_psw()
		)

		db.session.add(auth_token)
		db.session.commit()
		db.session.close()

		# imposto link
		_link = f"{Config.LINK_URL}:62233/buyer/reset_psw_token/{_token}/"
		_link = _link.replace("/:", ":")
		# print("LINK:", _link)

		try:
			# imposto e invio la mail con il link per il reset
			msg = Message(
				'Follow your request for change password in Consorzio Bue Grasso service.',
				sender="service@celerya.com",
				recipients=[form.email.data]
			)
			msg.body = f"This is the link for reset your password: \n\n{_link}\n\n" \
			           f"The link expiry in 15 min."
			mail.send(msg)
			flash("Richiesta reset password inviata correttamente.")
			return redirect(url_for("login_buyer", cert_nr=cert_nr))
		except Exception as err:
			flash(f"Richiesta reset password NON inviata: {err}.")
			return render_template("buyer/buyer_insert_email_reset_password.html", form=form, cert_nr=cert_nr)
	else:
		return render_template("buyer/buyer_insert_email_reset_password.html", form=form, cert_nr=cert_nr)


@app.route('/buyer/reset_psw_token/<_token>/')
def buyer_reset_psw_token(_token):
	_token = db.session.query(AuthToken).filter_by(token=_token).first()
	db.session.close()
	if datetime.now() > _token.expires_at:
		return "Il token è scaduto ripeti la procedura di ripristino password."
	else:
		_id = _token.user_id
		return redirect(url_for('buyer_reset_password', _id=_id))


@app.route("/buyer/reset_password/<_id>", methods=["GET", "POST"])
def buyer_reset_password(_id):
	"""Aggiorna password Utente Servizio."""
	form = FormPswReset()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		# _admin = json.loads(json.dumps(session["admin"]))

		new_password = psw_hash(form_data["new_password_1"].replace(" ", "").strip())
		# print("NEW:", new_password)

		_user = User.query.get(_id)

		if new_password == _user.password:
			session.clear()
			flash("La nuova password inserita è uguale a quella registrata.")
			return render_template("buyer/buyer_reset_password.html", form=form, id=_id)
		else:
			from ..routes.routes_event import event_create

			_user.password = new_password
			_user.updated_at = datetime.now()

			_user = _user.to_dict()

			db.session.query(User).filter_by(id=_id).update(_user)
			db.session.commit()

			flash(f"PASSWORD utente {_user['username']} resettata correttamente!")
			_event = {
				"executor": session["username"],
				"username": _user["username"],
				"Modification": "Password reset"
			}

			db.session.close()

			_event = event_create(_event, user_id=_id)
			if _event is not True:
				flash(_event)

			flash(f"PASSWORD utente {_user['username']} resettata correttamente!")
			return redirect(url_for('login_buyer', cert_nr="None"))
	else:
		return render_template("buyer/buyer_reset_password.html", form=form, id=_id)
