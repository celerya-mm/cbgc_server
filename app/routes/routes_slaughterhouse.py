import json

from flask import current_app as app, flash, redirect, render_template, url_for, request
from sqlalchemy.exc import IntegrityError

from app.app import db, session
from app.forms.form_slaughterhouse import FormSlaughterhouseCreate, FormSlaughterhouseUpdate
from app.models.heads import Head
from app.models.slaughterhouses import Slaughterhouse
from app.utilitys.functions import token_admin_validate, status_si_no

VIEW = "/slaughterhouse/view/"
VIEW_FOR = "slaughterhouse_view"
VIEW_HTML = "slaughterhouse/slaughterhouse_view.html"

CREATE = "/slaughterhouse/create/"
CREATE_FOR = "slaughterhouse_create"
CREATE_HTML = "slaughterhouse/slaughterhouse_create.html"

HISTORY = "/slaughterhouse/view/history/<int:_id>"
HISTORY_FOR = "slaughterhouse_view_history"
HISTORY_HTML = "slaughterhouse/slaughterhouse_view_history.html"

UPDATE = "/slaughterhouse/update/<int:_id>"
UPDATE_FOR = "slaughterhouse_update"
UPDATE_HTML = "slaughterhouse/slaughterhouse_update.html"


@app.route(VIEW, methods=["GET", "POST"])
@token_admin_validate
def slaughterhouse_view():
	"""Visualizzo informazioni Allevatori."""
	# Estraggo la lista degli allevatori
	_list = Slaughterhouse.query.all()
	_list = [r.to_dict() for r in _list]

	db.session.close()
	return render_template(VIEW_HTML, form=_list, create=CREATE_FOR, update=UPDATE_FOR, history=HISTORY_FOR)


@app.route(CREATE, methods=["GET", "POST"])
@token_admin_validate
def slaughterhouse_create():
	"""Creazione Allevatore Consorzio."""
	form = FormSlaughterhouseCreate()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		new_slaughterhouse = Slaughterhouse(
			slaughterhouse=form_data["slaughterhouse"].strip(),
			slaughterhouse_code=form_data["slaughterhouse_code"].strip(),
			email=form_data["email"].strip(),
			phone=form_data["phone"].strip(),
			address=form_data["address"].strip(),
			cap=form_data["cap"].strip(),
			city=form_data["city"].strip(),
			affiliation_start_date=form_data["affiliation_start_date"],
			affiliation_status=form_data["affiliation_status"],
			note=form_data["note"]
		)

		try:
			Slaughterhouse.create(new_slaughterhouse)
			flash("MACELLO creato correttamente.")
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
def slaughterhouse_view_history(_id):
	"""Visualizzo la storia delle modifiche al record utente Administrator."""
	from app.routes.routes_head import HISTORY_FOR as HEAD_HISTORY
	from app.routes.routes_farmer import HISTORY_FOR as FARMER_HISTORY
	from app.routes.routes_cert_cons import HISTORY_FOR as CERT_HISTORY
	from app.routes.routes_event import HISTORY_FOR as EVENT_HISTORY

	# Interrogo il DB
	slaughterhouse = Slaughterhouse.query.filter_by(id=_id).first()
	_slaughterhouse = slaughterhouse.to_dict()

	# Estraggo la storia delle modifiche per l'utente
	history_list = slaughterhouse.events
	history_list = [history.to_dict() for history in history_list]
	len_history = len(history_list)

	# estraggo i certificati del consorzio e i capi macellati
	cons_list = slaughterhouse.cons_cert
	_cons_list = [cert.to_dict() for cert in cons_list]

	head_list = []
	for cert in cons_list:
		_h = Head.query.get(cert.head_id)
		if _h and _h not in head_list:
			head_list.append(_h.to_dict())

	db.session.close()
	return render_template(
		HISTORY_HTML, form=_slaughterhouse, history_list=history_list, h_len=len_history,
		view=VIEW_FOR, update=UPDATE_FOR, cons_list=_cons_list, len_cons=len(_cons_list),
		head_list=head_list, len_heads=len(head_list), head=HEAD_HISTORY,
		cert_cons=CERT_HISTORY, farmer=FARMER_HISTORY, event_history=EVENT_HISTORY
	)


@app.route(UPDATE, methods=["GET", "POST"])
@token_admin_validate
def slaughterhouse_update(_id):
	"""Aggiorna dati Allevatore."""
	from app.routes.routes_event import event_create

	# recupero i dati del record
	slaughterhouse = Slaughterhouse.query.get(int(_id))
	form = FormSlaughterhouseUpdate(obj=slaughterhouse)

	if form.validate_on_submit():
		new_data = FormSlaughterhouseUpdate(request.form).to_dict()
		# print("NEW_DATA:", json.dumps(new_data, indent=2))

		previous_data = slaughterhouse.to_dict()
		previous_data.pop("updated_at")

		try:
			Slaughterhouse.update(_id, new_data)
			flash("MACELLO aggiornato correttamente.")
		except IntegrityError as err:
			db.session.rollback()
			db.session.close()
			flash(f"ERRORE: {str(err.orig)}")
			_info = {
				'created_at': slaughterhouse.created_at,
				'updated_at': slaughterhouse.updated_at,
			}
			return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)

		_event = {
			"username": session["username"],
			"table": Slaughterhouse.__tablename__,
			"Modification": f"Update Slaughterhouse whit id: {_id}",
			"Previous_data": previous_data
		}
		_event = event_create(_event, slaughterhouse_id=_id)
		return redirect(url_for(HISTORY_FOR, _id=_id))
	else:
		form.affiliation_status.data = status_si_no(slaughterhouse.affiliation_status)

		_info = {
			'created_at': slaughterhouse.created_at,
			'updated_at': slaughterhouse.updated_at,
		}
		db.session.close()
		return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)
