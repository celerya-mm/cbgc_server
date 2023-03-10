import json
import re
import folium
from flask import current_app as app, flash, redirect, render_template, url_for, request
from sqlalchemy.exc import IntegrityError

from app.app import db, session
from app.forms.form_farmer import FormFarmerCreate, FormFarmerUpdate
from app.models.farmers import Farmer
from app.utilitys.functions import token_admin_validate, status_true_false

VIEW = "/farmer/view/"
VIEW_FOR = "farmer_view"
VIEW_HTML = "farmer/farmer_view.html"

CREATE = "/farmer/create/"
CREATE_FOR = "farmer_create"
CREATE_HTML = "farmer/farmer_create.html"

HISTORY = "/farmer/view/history/<int:_id>"
HISTORY_FOR = "farmer_view_history"
HISTORY_HTML = "farmer/farmer_view_history.html"

UPDATE = "/farmer/update/<int:_id>"
UPDATE_FOR = "farmer_update"
UPDATE_HTML = "farmer/farmer_update.html"


def create_map(_list):
	"""Crea una mappa dalla base dati."""
	m = folium.Map(location=[44.48, 7.87], zoom_start=10, name="Mappa acquirenti Consorzio", tiles='Stamen Terrain')
	for record in _list:
		if record.coordinates and len(record.coordinates) > 5:
			if record.affiliation_status is False or record.affiliation_status in ["NO", "no"]:
				color = "red"  # rosso (macellerie)
				icon = "dollar"
			elif record.affiliation_status is True or record.affiliation_status in ["SI", "si"]:
				color = "green"  # blue (ristorante)
				icon = "dollar"
			else:
				color = "grey"  # grigio (manca il tipo)
				icon = "info-sign"

			coordinates = record.coordinates.split(", ")
			lat = re.findall(r'\d+\.\d+', coordinates[0].replace("(", ""))
			lat = float(lat[0])

			long = re.findall(r'\d+\.\d+', coordinates[1].replace(")", ""))
			long = float(long[0])

			html = "<style> " \
			       "h1 {font-size: 14px; color: #2B4692} " \
			       "p {font-size: 12px; color: #2B4692; margin: 5px} " \
			       "</style>" \
			       f"<h1>{record.stable_type}</h1>" \
			       f"<p><strong>Nome:</strong> {record.farmer_name}</p>" \
			       f"<p><strong>Indirizzo:</strong> {record.full_address}</p>" \
			       f"<p><strong>Telefono:</strong> {record.phone}</p>"

			iframe = folium.IFrame(html=html, ratio=0.2)
			popup = folium.Popup(iframe, max_width=300)

			tooltip = "Clicca!"

			folium.Marker(
				location=[lat, long], popup=popup, tooltip=tooltip, icon_size=(20, 20),
				icon=folium.Icon(color=color, prefix="fa", icon=icon)
			).add_to(m)

	return m._repr_html_()  # noqa


@app.route(VIEW, methods=["GET", "POST"])
@token_admin_validate
def farmer_view():
	"""Visualizzo informazioni Allevatori."""
	# Estraggo la lista degli allevatori
	_list = Farmer.query.all()

	m = create_map(_list)
	with open("./app/templates/map.html", "wb") as f:
		f.write(m.encode('utf-8'))

	_list = [r.to_dict() for r in _list]

	db.session.close()
	return render_template(VIEW_HTML, form=_list, create=CREATE_FOR, update=UPDATE_FOR, history=HISTORY_FOR)


@app.route(CREATE, methods=["GET", "POST"])
@token_admin_validate
def farmer_create():
	"""Creazione Allevatore Consorzio."""
	form = FormFarmerCreate()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
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
			Farmer.create(new_farmer)
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
	from app.routes.routes_cert_cons import HISTORY_FOR as CONS_HISTORY
	from app.routes.routes_head import HISTORY_FOR as HEAD_HISTORY, CREATE_FOR as HEAD_CREATE
	from app.routes.routes_cert_dna import HISTORY_FOR as DNA_HISTORY
	from app.routes.routes_event import HISTORY_FOR as EVENT_HISTORY

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

	db.session.close()
	return render_template(
		HISTORY_HTML, form=_farmer, view=VIEW_FOR, update=UPDATE_FOR,
		history_list=history_list, h_len=len(history_list), event_history=EVENT_HISTORY,
		cons_list=cons_list, len_cons=len(cons_list), cons_history=CONS_HISTORY,
		head_list=head_list, len_heads=len(head_list), head_history=HEAD_HISTORY, head_create=HEAD_CREATE,
		dna_list=dna_list, len_dna=len(dna_list), dna_history=DNA_HISTORY
	)


@app.route(UPDATE, methods=["GET", "POST"])
@token_admin_validate
def farmer_update(_id):
	"""Aggiorna dati Allevatore."""
	from app.routes.routes_event import event_create

	# recupero i dati del record
	farmer = Farmer.query.get(_id)
	form = FormFarmerUpdate(obj=farmer)

	if form.validate_on_submit():
		# recupero i dati e li converto in dict
		new_data = FormFarmerUpdate(request.form).to_dict()
		# print("NEW_DATA:", json.dumps(new_data, indent=2)

		previous_data = farmer.to_dict()
		previous_data.pop("updated_at")

		try:
			Farmer.update(_id, new_data)
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
		_event = event_create(_event, farmer_id=_id)
		return redirect(url_for(HISTORY_FOR, _id=_id))
	else:
		_info = {
			'created_at': farmer.created_at,
			'updated_at': farmer.updated_at,
		}
		db.session.close()
		return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)
