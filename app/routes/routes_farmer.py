import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db, session
from ..forms.form_farmer import FormFarmerCreate, FormFarmerUpdate
from ..models.farmers import Farmer
from ..utilitys.functions import (token_admin_validate, status_true_false, str_to_date, status_si_no,
                                  address_mount, not_empty)

VIEW = "/farmer/view/"
VIEW_FOR = "farmer_view"
VIEW_HTML = "farmer/farmer_view.html"

CREATE = "/farmer/create/"
CREATE_FOR = "farmer_create"
CREATE_HTML = "farmer/farmer_create.html"

HISTORY = "/farmer/view/history/<_id>"
HISTORY_FOR = "farmer_view_history"
HISTORY_HTML = "farmer/farmer_view_history.html"

UPDATE = "/farmer/update/<_id>"
UPDATE_FOR = "farmer_update"
UPDATE_HTML = "farmer/farmer_update.html"


@app.route(VIEW, methods=["GET", "POST"])
@token_admin_validate
def farmer_view():
	"""Visualizzo informazioni Allevatori."""
	# Estraggo la lista degli allevatori
	_list = Farmer.query.all()
	_list = [r.to_dict() for r in _list]

	for _dict in _list:
		_dict["maps"] = f'{_dict["cap"].strip().replace(" ", "")},' \
		                f'{_dict["address"].strip().replace(" ", "+")}' \
		                f',{_dict["city"].strip().replace(" ", "+")}'

	db.session.close()
	return render_template(VIEW_HTML, form=_list, create=CREATE_FOR, update=UPDATE_FOR, history=HISTORY_FOR)


@app.route(CREATE, methods=["GET", "POST"])
@token_admin_validate
def farmer_create():
	"""Creazione Allevatore Consorzio."""
	form = FormFarmerCreate()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		# print("FARMER_FORM_DATA", json.dumps(form_data, indent=2))

		new_farmer = Farmer(
			farmer_name=form_data["farmer_name"].strip(),

			email=form_data["email"].strip(),
			phone=form_data["phone"].strip(),

			address=form_data["address"].strip(),
			cap=form_data["cap"].strip(),
			city=form_data["city"].strip(),

			affiliation_start_date=form_data["affiliation_start_date"],
			affiliation_status=status_true_false(form_data["affiliation_status"]),

			stable_code=form_data["stable_code"],
			stable_type=form_data["stable_type"],
			stable_productive_orientation=form_data["stable_productive_orientation"],
			stable_breeding_methods=form_data["stable_breeding_methods"],

			note=form_data["note"].strip()
		)
		try:
			db.session.add(new_farmer)
			db.session.commit()
			db.session.close()
			flash("ALLEVATORE creato correttamente.")
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
def farmer_view_history(_id):
	"""Visualizzo la storia delle modifiche al record utente Administrator."""
	from ..routes.routes_cert_cons import HISTORY_FOR as CONS_HISTORY
	from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY
	from ..routes.routes_cert_dna import HISTORY_FOR as DNA_HISTORY
	from ..routes.routes_event import HISTORY_FOR as EVENT_HISTORY

	# Interrogo il DB
	farmer = Farmer.query.get(int(_id))
	_farmer = farmer.to_dict()

	# Estraggo la storia delle modifiche per l'utente
	history_list = farmer.events
	history_list = [history.to_dict() for history in history_list]

	# Estraggo l'elenco dei capi dell' Allevatore
	head_list = farmer.heads
	head_list = [head.to_dict() for head in head_list]

	# Estraggo l'elenco dei certificati
	cons_list = farmer.cons_certs
	cons_list = [cert.to_dict() for cert in cons_list]

	# Estraggo l'elenco dei DNA
	dna_list = farmer.dna_certs
	dna_list = [dna.to_dict() for dna in dna_list]

	_farmer["maps"] = f'{_farmer["cap"].strip().replace(" ", "")},' \
	                  f'{_farmer["address"].strip().replace(" ", "+")}' \
	                  f',{_farmer["city"].strip().replace(" ", "+")}'

	db.session.close()
	return render_template(
		HISTORY_HTML, form=_farmer, view=VIEW_FOR, update=UPDATE_FOR,
		history_list=history_list, h_len=len(history_list), event_history=EVENT_HISTORY,
		cons_list=cons_list, len_cons=len(cons_list), cons_history=CONS_HISTORY,
		head_list=head_list, len_heads=len(head_list), head_history=HEAD_HISTORY,
		dna_list=dna_list, len_dna=len(dna_list), dna_history=DNA_HISTORY
	)


@app.route(UPDATE, methods=["GET", "POST"])
@token_admin_validate
def farmer_update(_id):
	"""Aggiorna dati Allevatore."""
	from ..routes.routes_event import event_create

	form = FormFarmerUpdate()
	if form.validate_on_submit():
		# recupero i dati e li converto in dict
		new_data = json.loads(json.dumps(request.form))
		new_data.pop('csrf_token', None)
		# print("FORM_DATA_PASS:", json.dumps(new_data, indent=2))

		farmer = Farmer.query.get(_id)
		previous_data = farmer.to_dict()
		previous_data.pop("updated_at")
		# print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

		new_data["full_address"] = address_mount(new_data["address"], new_data["cap"], new_data["city"])
		new_data["affiliation_start_date"] = str_to_date(new_data["affiliation_start_date"])
		new_data["affiliation_end_date"] = str_to_date(new_data["affiliation_end_date"])
		new_data["affiliation_status"] = status_true_false(new_data["affiliation_status"])

		new_data["phone"] = not_empty(new_data["phone"])
		new_data["email"] = not_empty(new_data["email"])
		new_data["stable_code"] = not_empty(new_data["stable_code"])

		new_data["note"] = not_empty(new_data["note"])

		new_data["created_at"] = farmer.created_at
		new_data["updated_at"] = datetime.now()

		# print("NEW_DATA:", new_data)
		try:
			db.session.query(Farmer).filter_by(id=_id).update(new_data)
			db.session.commit()
			flash("ALLEVATORE aggiornato correttamente.")
		except IntegrityError as err:
			db.session.rollback()
			db.session.close()
			flash(f"ERRORE: {str(err.orig)}")
			_info = {
				'created_at': farmer.created_at,
				'updated_at': farmer.updated_at,
			}
			return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)

		_event = {
			"username": session["username"],
			"table": Farmer.__tablename__,
			"Modification": f"Update Farmer whit id: {_id}",
			"Previous_data": previous_data
		}
		# print("EVENT:", json.dumps(_event, indent=2))

		_event = event_create(_event, farmer_id=_id)
		if _event is True:
			return redirect(url_for(HISTORY_FOR, _id=_id))
		else:
			flash(_event)
			return redirect(url_for(HISTORY_FOR, _id=_id))
	else:
		# recupero i dati del record
		farmer = Farmer.query.get(_id)

		form.farmer_name.data = farmer.farmer_name
		form.email.data = farmer.email
		form.phone.data = farmer.phone

		form.address.data = farmer.address
		form.cap.data = farmer.cap
		form.city.data = farmer.city

		form.stable_code.data = farmer.stable_code
		form.stable_type.data = farmer.stable_type

		form.stable_productive_orientation.data = farmer.stable_productive_orientation
		form.stable_breeding_methods.data = farmer.stable_breeding_methods

		form.affiliation_start_date.data = str_to_date(farmer.affiliation_start_date)
		form.affiliation_end_date.data = str_to_date(farmer.affiliation_end_date)
		form.affiliation_status.data = status_si_no(farmer.affiliation_status)

		form.note.data = farmer.note

		_info = {
			'created_at': farmer.created_at,
			'updated_at': farmer.updated_at,
		}
		# print("FARMER_:", form)
		# print("FARMER_FORM:", json.dumps(form.to_dict(form), indent=2))
		db.session.close()
		return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)
