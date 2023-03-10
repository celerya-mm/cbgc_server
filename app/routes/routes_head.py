import json

from flask import current_app as app, flash, redirect, render_template, url_for, request
from sqlalchemy.exc import IntegrityError

from app.app import db, session
from app.forms.form_head import FormHeadCreate, FormHeadUpdate
from app.models.buyers import Buyer
from app.models.farmers import Farmer
from app.models.heads import Head
from app.models.slaughterhouses import Slaughterhouse
from app.utilitys.functions import not_empty, str_to_date, dict_group_by, token_admin_validate

VIEW = "/head/view/"
VIEW_FOR = "head_view"
VIEW_HTML = "head/head_view.html"

CREATE = "/head/create/<int:f_id>/"
CREATE_FOR = "head_create"
CREATE_HTML = "head/head_create.html"

HISTORY = "/head/view/history/<int:_id>"
HISTORY_FOR = "head_view_history"
HISTORY_HTML = "head/head_view_history.html"

UPDATE = "/head/update/<int:_id>"
UPDATE_FOR = "head_update"
UPDATE_HTML = "head/head_update.html"


@app.route(VIEW, methods=["GET", "POST"])
@token_admin_validate
def head_view():
	"""Visualizzo informazioni Capi."""
	from app.routes.routes_farmer import HISTORY_FOR as FARMER_HISTORY

	if request.method == 'POST':
		birth_year = request.form.get('birth_year') or "*"
		sale_year = request.form.get('sale_year') or "*"
		print(birth_year, sale_year)
		if birth_year != "*" and sale_year != "*":
			_list = Head.query.filter_by(birth_year=int(birth_year), sale_year=sale_year).all()
		elif birth_year != "*":
			_list = Head.query.filter_by(birth_year=int(birth_year)).all()
		elif sale_year != "*":
			_list = Head.query.filter_by(sale_year=int(sale_year)).all()
		else:
			_list = Head.query.all()
			flash(f"Nessun Anno selezionato, mostro tutti i records: {len(_list)}")

		flash(f"Capi trovati: {len(_list)}")
		if len(_list) == 0:
			flash(f"Nessun Capo presente con i parametri cercati. Mostro tutti i records.")
			return redirect(url_for(VIEW_FOR))
	else:
		_list = Head.query.all()

	db.session.close()

	_list = [r.to_dict() for r in _list]

	# raggruppa per anno di nascita
	group_birth = dict_group_by(_list, "birth_year", year=True)
	birth_labels = [sub["birth_year"] for sub in group_birth]
	birth_values = [sub['number'] for sub in group_birth]

	# raggruppa per anno di nascita e conformit?? castrazione
	group_conf = dict_group_by(_list, group_d="birth_year", group_f="castration_compliance", year=True)
	conf_labels = [sub["birth_year"] for sub in group_conf if sub["castration_compliance"] is True]
	conf_values = [sub['number'] for sub in group_conf if sub["castration_compliance"] is True]
	not_conf_values = [sub['number'] for sub in group_conf if sub["castration_compliance"] is False]

	# raggruppa per anno vendita
	group_sale = dict_group_by(_list, "sale_year", year=True)
	sale_labels = [sub["sale_year"] for sub in group_sale]
	sale_values = [sub['number'] for sub in group_sale]

	# raggruppa per allevatori
	group_farmer = dict_group_by(_list, "farmer_id")
	farmer_labels = [sub["farmer_id"] for sub in group_farmer]
	farmer_values = [sub['number'] for sub in group_farmer]

	return render_template(
		VIEW_HTML, form=_list, create=CREATE_FOR, update=UPDATE_FOR, history=HISTORY_FOR, farmer=FARMER_HISTORY,
		birth_labels=json.dumps(birth_labels), birth_values=json.dumps(birth_values),
		conf_labels=json.dumps(conf_labels), conf_values=json.dumps(conf_values),
		not_conf_values=json.dumps(not_conf_values),
		sale_labels=json.dumps(sale_labels), sale_values=json.dumps(sale_values),
		farmer_labels=json.dumps(farmer_labels), farmer_values=json.dumps(farmer_values)
	)


@app.route(CREATE, methods=["GET", "POST"])
@token_admin_validate
def head_create(f_id):
	"""Creazione Capo Consorzio."""
	from app.routes.routes_farmer import HISTORY_FOR as FARMER_HISTORY

	form = FormHeadCreate.new()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		new_head = Head(
			headset=form_data["headset"],
			birth_date=str_to_date(form_data["birth_date"]),
			castration_date=str_to_date(form_data["castration_date"]),
			slaughter_date=str_to_date(form_data["slaughter_date"]),
			sale_date=str_to_date(form_data["sale_date"]),
			farmer_id=form_data["farmer_id"].split(" - ")[0],
			note=not_empty(form_data["note"].strip())
		)

		try:
			Head.create(new_head)
			flash("CAPO creato correttamente.")
			return redirect(url_for(VIEW_FOR))
		except IntegrityError as err:
			db.session.rollback()
			db.session.close()
			flash(f"ERRORE: {str(err.orig)}")
			return render_template(CREATE_HTML, form=form, view=VIEW_FOR)
	else:
		_farmer = Farmer.query.get(f_id)
		form.farmer_id.data = f"{_farmer.id} - {_farmer.farmer_name}"
		db.session.close()
		return render_template(CREATE_HTML, form=form, view=VIEW_FOR, farmer=FARMER_HISTORY, f_id=f_id)


@app.route(HISTORY, methods=["GET", "POST"])
@token_admin_validate
def head_view_history(_id):
	"""Visualizzo la storia delle modifiche al record del Capo."""
	from app.routes.routes_cert_dna import HISTORY_FOR as DNA_HISTORY, CREATE_FOR as DNA_CREATE_FOR
	from app.routes.routes_buyer import HISTORY_FOR as BUYER_HISTORY
	from app.routes.routes_farmer import HISTORY_FOR as FARMER_HISTORY
	from app.routes.routes_cert_cons import HISTORY_FOR as CERT_HISTORY, CREATE_FOR as CONS_CREATE_FOR
	from app.routes.routes_slaughterhouse import HISTORY_FOR as SLAUG_HISTORY
	from app.routes.routes_event import HISTORY_FOR as EVENT_HISTORY

	head = Head.query.get(int(_id))
	_head = head.to_dict()

	if head.farmer_id:
		farmer = Farmer.query.get(head.farmer_id)
		_head["farmer_id"] = f"{farmer.id} - {farmer.farmer_name}"

	# Estraggo la storia delle modifiche per l'utente
	history_list = head.events
	history_list = [history.to_dict() for history in history_list]

	# estraggo il certificato DNA
	dna_list = head.dna_cert
	dna_list = [dna.to_dict() for dna in dna_list]

	# estraggo i certificati del consorzio, i compratori e i macelli
	cons_list = head.cons_cert
	_cons_list = [cert.to_dict() for cert in cons_list]

	buyer_list = []
	for cert in cons_list:
		_b = Buyer.query.get(cert.buyer_id)
		if _b and _b not in buyer_list:
			_b = _b.to_dict()
			buyer_list.append(_b)

	slaug_list = []
	for cert in cons_list:
		_s = Slaughterhouse.query.get(cert.slaughterhouse_id)
		if _s and _s not in slaug_list:
			slaug_list.append(_s.to_dict())

	db.session.close()
	return render_template(
		HISTORY_HTML, form=_head, history_list=history_list, h_len=len(history_list), view=VIEW_FOR,
		update=UPDATE_FOR, _id_farm=head.farmer_id, farm_history=FARMER_HISTORY,
		dna_list=dna_list, len_dna=len(dna_list), dna_history=DNA_HISTORY, dna_create=DNA_CREATE_FOR,
		cons_list=_cons_list, len_cons=len(_cons_list), cons_history=CERT_HISTORY, cons_create=CONS_CREATE_FOR,
		buyer_list=buyer_list, len_buyers=len(buyer_list), buyer_history=BUYER_HISTORY,
		slaug_list=slaug_list, len_slaug=len(slaug_list), slaug_history=SLAUG_HISTORY,
		event_history=EVENT_HISTORY
	)


@app.route(UPDATE, methods=["GET", "POST"])
@token_admin_validate
def head_update(_id):
	"""Aggiorna dati Capo."""
	from app.routes.routes_cert_dna import CREATE_FOR as DNA_CREATE_FOR
	from app.routes.routes_event import event_create

	# recupero i dati del record
	head = Head.query.get(int(_id))
	form = FormHeadUpdate.new(obj=head)

	if form.validate_on_submit():
		new_data = FormHeadUpdate(request.form).to_dict()
		# print("NEW_DATA:", json.dumps(new_data, indent=2))

		previous_data = head.to_dict()
		previous_data.pop("updated_at")

		try:
			Head.update(_id, new_data)
			flash("CAPO aggiornato correttamente.")
		except IntegrityError as err:
			db.session.rollback()
			db.session.close()
			flash(f"ERRORE: {str(err.orig)}")
			_info = {
				'created_at': head.created_at,
				'updated_at': head.updated_at,
			}
			return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR,
			                       f_id=new_data["farmer_id"])

		_event = {
			"username": session["username"],
			"table": Head.__tablename__,
			"Modification": f"Update Head whit id: {_id}",
			"Previous_data": previous_data
		}
		_event = event_create(_event, head_id=_id)
		return redirect(url_for(HISTORY_FOR, _id=_id))
	else:
		farmer = Farmer.query.get(head.farmer_id)
		form.farmer_id.data = f"{farmer.id} - {farmer.farmer_name}"

		_info = {
			'created_at': head.created_at,
			'updated_at': head.updated_at,
		}
		db.session.close()
		return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR, f_id=head.farmer_id,
		                       dna_create=DNA_CREATE_FOR)
