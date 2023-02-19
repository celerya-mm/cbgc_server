import json

from flask import current_app as app, flash, redirect, render_template, url_for, request
from sqlalchemy.exc import IntegrityError

from app.app import db, session
from app.forms.form_cert_dna import FormCertDnaCreate, FormCertDnaUpdate
from app.models.certificates_dna import CertificateDna
from app.models.farmers import Farmer
from app.models.heads import Head
from app.utilitys.functions import token_admin_validate, not_empty

VIEW = "/cert_dna/view/"
VIEW_FOR = "cert_dna_view"
VIEW_HTML = "cert_dna/cert_dna_view.html"

CREATE = "/cert_dna/create/<int:h_id>/<f_id>/<h_set>/"
CREATE_FOR = "cert_dna_create"
CREATE_HTML = "cert_dna/cert_dna_create.html"

HISTORY = "/cert_dna/view/history/<int:_id>"
HISTORY_FOR = "cert_dna_view_history"
HISTORY_HTML = "cert_dna/cert_dna_view_history.html"

UPDATE = "/cert_dna/update/<int:_id>"
UPDATE_FOR = "cert_dna_update"
UPDATE_HTML = "cert_dna/cert_dna_update.html"


@app.route(VIEW, methods=["GET", "POST"])
@token_admin_validate
def cert_dna_view():
	"""Visualizzo informazioni Certificato."""
	from app.routes.routes_head import HISTORY_FOR as HEAD_HISTORY
	from app.routes.routes_farmer import HISTORY_FOR as FARMER_HISTORY

	# Estraggo la lista dei certificati DNA
	_list = CertificateDna.query.all()
	_list = [r.to_dict() for r in _list]

	db.session.close()
	return render_template(
		VIEW_HTML, form=_list, create=CREATE_FOR, update=UPDATE_FOR, history=HISTORY_FOR,
		farmer=FARMER_HISTORY, head=HEAD_HISTORY
	)


@app.route(CREATE, methods=["GET", "POST"])
@token_admin_validate
def cert_dna_create(h_id, f_id, h_set):
	"""Creazione Certificato DNA."""
	from app.routes.routes_head import HISTORY_FOR as HEAD_HISTORY

	form = FormCertDnaCreate.new()

	if form.validate_on_submit():
		try:
			form_data = json.loads(json.dumps(request.form))

			new_data = CertificateDna(
				dna_cert_id=form_data["dna_cert_id"].strip(),
				dna_cert_date=form_data["dna_cert_date"],
				veterinarian=not_empty(form_data["veterinarian"].strip()),
				head_id=h_id,
				farmer_id=int(f_id.split(" - ")[0]),
				note=not_empty(form_data["note"].strip())
			)

			CertificateDna.create(new_data)
			flash("CERTIFICATO DNA creato correttamente.")
			return redirect(url_for(HEAD_HISTORY, _id=h_id))
		except IntegrityError as err:
			db.session.rollback()
			db.session.close()
			flash(f"ERRORE: {str(err.orig)}")
			return render_template(CREATE_HTML, form=form, f_id=f_id, h_set=h_set, h_id=h_id, head_history=HEAD_HISTORY)
	else:
		h_set = f"{int(h_id)} - {h_set}"
		return render_template(CREATE_HTML, form=form, f_id=f_id, h_set=h_set, h_id=h_id, head_history=HEAD_HISTORY)


@app.route(HISTORY, methods=["GET", "POST"])
@token_admin_validate
def cert_dna_view_history(_id):
	"""Visualizzo la storia delle modifiche al record utente Administrator."""
	from app.routes.routes_event import HISTORY_FOR as EVENT_HISTORY
	from app.routes.routes_head import HISTORY_FOR as HEAD_HISTORY
	from app.routes.routes_farmer import HISTORY_FOR as FARMER_HISTORY

	# Estraggo l' ID dell'utente corrente
	session["id_user"] = _id

	# Interrogo il DB
	cert_dna = CertificateDna.query.get(_id)
	_cert_dna = cert_dna.to_dict()

	# estraggo capo
	_head = Head.query.get(cert_dna.head_id)
	_head = _head.to_dict()
	h_id = int(_head['id'])
	_cert_dna['head_id'] = f"{_head['id']} - {_head['headset']}"

	# estraggo allevatore
	_farmer = Farmer.query.get(cert_dna.farmer_id)
	_farmer = _farmer.to_dict()
	f_id = int(_farmer['id'])
	_cert_dna['farmer_id'] = f"{_farmer['id']} - {_farmer['farmer_name']}"

	# Estraggo la storia delle modifiche
	history_list = cert_dna.events
	history_list = [history.to_dict() for history in history_list]
	len_history = len(history_list)

	db.session.close()
	return render_template(
		HISTORY_HTML, form=_cert_dna, history_list=history_list, h_len=len_history, view=VIEW_FOR, update=UPDATE_FOR,
		head=h_id, view_head=HEAD_HISTORY, _id=_id, farmer=f_id, view_farmer=FARMER_HISTORY, event_history=EVENT_HISTORY
	)


@app.route(UPDATE, methods=["GET", "POST"])
@token_admin_validate
def cert_dna_update(_id):
	"""Aggiorna dati Certificato DNA."""
	from app.routes.routes_event import event_create

	# recupero i dati
	_cert = CertificateDna.query.get(_id)
	form = FormCertDnaUpdate.new(obj=_cert)

	if form.validate_on_submit():
		from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY_FOR

		new_data = FormCertDnaUpdate(request.form).to_dict()
		print("NEW_DATA:", json.dumps(new_data, indent=2))

		previous_data = _cert.to_dict()
		previous_data.pop("updated_at")

		try:
			CertificateDna.update(_id, new_data)
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
		_event = event_create(_event, cert_dna_id=_id)
		return redirect(url_for(HEAD_HISTORY_FOR, _id=new_data["head_id"]))
	else:
		# recupera Capo
		_head = Head.query.get(_cert.head_id)
		# recupera Allevatore
		_farmer = Farmer.query.get(_cert.farmer_id)

		form.head_id.data = f"{_head.id} - {_head.headset}"
		form.farmer_id.data = f"{_farmer.id} - {_farmer.farmer_name}"

		_info = {
			'created_at': _cert.created_at,
			'updated_at': _cert.updated_at,
		}
		db.session.close()
		return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)
