import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db, session
from ..forms.form_cert_dna import FormCertDnaCreate, FormCertDnaUpdate, list_head, list_farmer
from ..models.certificates_dna import CertificateDna
from ..models.farmers import Farmer
from ..models.heads import Head
from ..utilitys.functions import event_create, token_admin_validate, year_extract

VIEW = "/cert_dna/view/"
VIEW_FOR = "cert_dna_view"
VIEW_HTML = "cert_dna/cert_dna_view.html"

CREATE = "/cert_dna/create/<h_id>/<f_id>/<h_set>/"
CREATE_FOR = "cert_dna_create"
CREATE_HTML = "cert_dna/cert_dna_create.html"

HISTORY = "/cert_dna/view/history/<_id>"
HISTORY_FOR = "cert_dna_view_history"
HISTORY_HTML = "cert_dna/cert_dna_view_history.html"

UPDATE = "/cert_dna/update/<_id>"
UPDATE_FOR = "cert_dna_update"
UPDATE_HTML = "cert_dna/cert_dna_update.html"


@app.route(VIEW, methods=["GET", "POST"])
@token_admin_validate
def cert_dna_view():
	"""Visualizzo informazioni Certificato."""
	# Estraggo la lista degli utenti amministratori
	_list = CertificateDna.query.all()
	db.session.close()
	_list = [r.to_dict() for r in _list]
	return render_template(VIEW_HTML, form=_list, create=CREATE_FOR, update=UPDATE_FOR, history=HISTORY_FOR)


@app.route(CREATE, methods=["GET", "POST"])
@token_admin_validate
def cert_dna_create(h_id, f_id, h_set):
	"""Creazione Certificato DNA."""
	from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY_FOR

	form = FormCertDnaCreate()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		# print("DNA_FORM_DATA", json.dumps(form_data, indent=2))

		new_data = CertificateDna(
			dna_cert_id=form_data["dna_cert_id"].strip(),
			dna_cert_date=form_data["dna_cert_date"],
			veterinarian=form_data["veterinarian"].strip(),
			head_id=int(h_id),
			farmer_id=int(f_id.split(" - ")[0]),
			note=form_data["note"].strip()
		)
		# print("NEW_DATA:", json.dumps(new_data.to_dict(), indent=2))
		try:
			db.session.add(new_data)
			db.session.commit()
			db.session.close()
			flash("CERTIFICATO DNA creato correttamente.")
			return redirect(url_for(VIEW_FOR))
		except IntegrityError as err:
			db.session.rollback()
			db.session.close()
			flash(f"ERRORE: {str(err.orig)}")
			return render_template(CREATE_HTML, form=form, f_id=f_id, h_set=h_set, h_id=h_id,
			                       head_history=HEAD_HISTORY_FOR)
	else:
		h_set = f"{int(h_id)} - {h_set}"
		return render_template(CREATE_HTML, form=form, f_id=f_id, h_set=h_set, h_id=h_id, head_history=HEAD_HISTORY_FOR)


@app.route(HISTORY, methods=["GET", "POST"])
@token_admin_validate
def cert_dna_view_history(_id):
	"""Visualizzo la storia delle modifiche al record utente Administrator."""
	from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY_FOR
	from ..routes.routes_farmer import HISTORY_FOR as FARMER_HISTORY_FOR
	from ..routes.routes_event import HISTORY_FOR as EVENT_HISTORY

	# Estraggo l' ID dell'utente corrente
	session["id_user"] = _id

	# Interrogo il DB
	cert_dna = CertificateDna.query.get(_id)
	_cert_dna = cert_dna.to_dict()

	# estraggo capo
	_head = Head.query.get(cert_dna.head_id)
	_head = _head.to_dict()

	# estraggo allevatore
	_farmer = Farmer.query.get(cert_dna.farmer_id)
	_farmer = _farmer.to_dict()

	# Estraggo la storia delle modifiche
	history_list = cert_dna.events
	history_list = [history.to_dict() for history in history_list]
	len_history = len(history_list)
	db.session.close()
	return render_template(HISTORY_HTML, form=_cert_dna, history_list=history_list, h_len=len_history, view=VIEW_FOR,
	                       update=UPDATE_FOR, head=_head, view_head=HEAD_HISTORY_FOR, _id=_id,
	                       farmer=_farmer, view_farmer=FARMER_HISTORY_FOR, event_history=EVENT_HISTORY)


@app.route(UPDATE, methods=["GET", "POST"])
@token_admin_validate
def cert_dna_update(_id):
	"""Aggiorna dati Utente."""
	form = FormCertDnaUpdate()
	if form.validate_on_submit():
		from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY_FOR

		new_data = json.loads(json.dumps(request.form))
		new_data.pop('csrf_token', None)
		# print("USER_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

		_cert = CertificateDna.query.get(_id)
		db.session.close()
		previous_data = _cert.to_dict()
		# print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

		if new_data["head_id"] not in list_head():
			flash(f'Attenzione non è presente nessun Capo con ID: {new_data["head_id"]}')
			_info = {
				'created_at': _cert.created_at,
				'updated_at': _cert.updated_at,
			}
			return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR, h_id=_id)
		else:
			new_data["head_id"] = new_data["head_id"].split(" - ")[0]

		if new_data["farmer_id"] not in list_farmer():
			flash(f'Attenzione non è presente nessun Allevatore con ID: {new_data["farmer_id"]}')
			_info = {
				'created_at': _cert.created_at,
				'updated_at': _cert.updated_at,
			}
			return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR, h_id=_id)
		else:
			new_data["farmer_id"] = new_data["farmer_id"].split(" - ")[0]

		new_data["dna_cert_year"] = year_extract(new_data["dna_cert_date"])
		new_data["dna_cert_nr"] = f'{new_data["dna_cert_id"]}/{new_data["dna_cert_year"]}'

		new_data["created_at"] = _cert.created_at
		new_data["updated_at"] = datetime.now()

		# print("NEW_DATA:", new_data)
		try:
			db.session.query(CertificateDna).filter_by(id=_id).update(new_data)
			db.session.commit()
			db.session.close()
			flash("CERTIFICATO aggiornato correttamente.")
		except IntegrityError as err:
			db.session.rollback()
			db.session.close()
			flash(f"ERRORE: {str(err.orig)}")
			_info = {
				'created_at': _cert.created_at,
				'updated_at': _cert.updated_at,
			}
			return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)

		_event = {
			"username": session["username"],
			"table": CertificateDna.__tablename__,
			"Modification": f"Update Certificate DNA whit id: {_id}",
			"Previous_data": previous_data
		}
		# print("EVENT:", json.dumps(_event, indent=2))
		if event_create(_event, cert_dna_id=_id):
			return redirect(url_for(HEAD_HISTORY_FOR, _id=new_data["head_id"]))
		else:
			flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
			return redirect(url_for(HEAD_HISTORY_FOR, _id=new_data["head_id"]))
	else:
		# recupero i dati
		_cert = CertificateDna.query.get(_id)
		# print("USER:", user)
		# print("USER_FIND:", json.dumps(user.to_dict(), indent=2))

		# recupera Capo
		_head = Head.query.get(_cert.head_id)
		# recupera Allevatore
		_farmer = Farmer.query.get(_cert.farmer_id)

		db.session.close()

		form.dna_cert_id.data = _id
		form.dna_cert_date.data = _cert.dna_cert_date
		form.veterinarian.data = _cert.veterinarian

		form.head_id.data = f"{_head.id} - {_head.headset}"
		form.farmer_id.data = f"{_farmer.id} - {_farmer.farmer_name}"

		form.note.data = _cert.note

		_info = {
			'created_at': _cert.created_at,
			'updated_at': _cert.updated_at,
		}
		# print("DNA_UPDATE:", json.dumps(form.to_dict(), indent=2))
		return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)
