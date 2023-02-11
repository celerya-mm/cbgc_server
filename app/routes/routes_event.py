import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, url_for
from sqlalchemy.exc import IntegrityError

from ..app import db, session
from ..models.events_db import EventDB

from ..models.accounts import Administrator, User
from ..models.farmers import Farmer
from ..models.buyers import Buyer
from ..models.slaughterhouses import Slaughterhouse
from ..models.heads import Head
from ..models.certificates_cons import CertificateCons
from ..models.certificates_dna import CertificateDna
from ..utilitys.functions import token_admin_validate, date_to_str

HISTORY = "/event/view/history/<int:_id>/"
HISTORY_FOR = "event_view_history"
HISTORY_HTML = "event/event_view_history.html"

RESTORE = "/event/restore/<int:_id>/<int:id_record>/<table>/<view_for>/"
RESTORE_FOR = "event_restore"


def event_create(event, admin_id=None, user_id=None, farmer_id=None, buyer_id=None,
                 slaughterhouse_id=None, head_id=None, cert_cons_id=None, cert_dna_id=None):
	"""Registro evento DB."""
	try:
		new_event = EventDB(
			event=event,
			admin_id=admin_id,
			user_id=user_id,
			farmer_id=farmer_id,
			buyer_id=buyer_id,
			slaughterhouse_id=slaughterhouse_id,
			head_id=head_id,
			cert_cons_id=cert_cons_id,
			cert_dna_id=cert_dna_id
		)

		EventDB.create(new_event)
		print("EVENT_CREATED.")
		return True
	except IntegrityError as err:
		db.session.close()
		if "duplicate key value violates unique constraint" in str(err):
			return True
		else:
			print("INTEGRITY_ERROR_EVENT:", str(err))
			flash(err)
			return str(err)
	except Exception as err:
		db.session.close()
		print("ERROR_REGISTR_EVENT:", str(err))
		flash(err)
		return str(err)


@app.route(HISTORY, methods=["GET", "POST"])
@token_admin_validate
def event_view_history(_id):
	"""Visualizzo la storia delle modifiche al record utente Administrator."""
	from ..routes.routes_admin import HISTORY_FOR as ADMIN_HISTORY_FOR
	from ..routes.routes_user import HISTORY_FOR as USER_HISTORY_FOR
	from ..routes.routes_farmer import HISTORY_FOR as FARMER_HISTORY_FOR
	from ..routes.routes_buyer import HISTORY_FOR as BUYER_HISTORY_FOR
	from ..routes.routes_slaughterhouse import HISTORY_FOR as SLAUG_HISTORY_FOR
	from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY_FOR
	from ..routes.routes_cert_cons import HISTORY_FOR as CERT_HISTORY_FOR
	from ..routes.routes_cert_dna import HISTORY_FOR as DNA_HISTORY_FOR

	# Estraggo l' ID dell'utente corrente
	session["event_id"] = _id

	# Interrogo il DB
	event = EventDB.query.get(_id)
	_event = event.to_dict()

	# estraggo record collegato
	if event.admin_id:
		related = Administrator.query.get(event.admin_id)
		related = related.to_dict()
		field = "admin_id"
		table = Administrator.__tablename__
		id_related = related["id"]
		type_related = "Amministratori"
		view_related = ADMIN_HISTORY_FOR
	elif event.user_id:
		related = User.query.get(event.user_id)
		related = related.to_dict()
		field = "user_id"
		table = User.__tablename__
		id_related = related["id"]
		type_related = "Utenti"
		view_related = USER_HISTORY_FOR
	elif event.farmer_id:
		related = Farmer.query.get(event.farmer_id)
		related = related.to_dict()
		field = "head_id"
		table = Farmer.__tablename__
		id_related = related["id"]
		type_related = "Allevatori"
		view_related = FARMER_HISTORY_FOR
	elif event.buyer_id:
		related = Buyer.query.get(event.buyer_id)
		related = related.to_dict()
		field = "buyer_id"
		table = Buyer.__tablename__
		id_related = related["id"]
		type_related = "Acquirenti"
		view_related = BUYER_HISTORY_FOR
	elif event.slaughterhouse_id:
		related = Slaughterhouse.query.get(event.slaughterhouse_id)
		related = related.to_dict()
		field = "slaughterhouse_id"
		table = Slaughterhouse.__tablename__
		id_related = related["id"]
		type_related = "Macelli"
		view_related = SLAUG_HISTORY_FOR
	elif event.head_id:
		related = Head.query.get(event.head_id)
		related = related.to_dict()
		field = "head_id"
		table = Head.__tablename__
		id_related = related["id"]
		type_related = "Capi"
		view_related = HEAD_HISTORY_FOR
	elif event.cert_cons_id:
		related = CertificateCons.query.get(event.cert_cons_id)
		related = related.to_dict()
		field = "cert_cons_id"
		table = CertificateCons.__tablename__
		id_related = related["id"]
		type_related = "Certificati Consorzio"
		view_related = CERT_HISTORY_FOR
	else:
		related = CertificateDna.query.get(event.cert_dna_id)
		related = related.to_dict()
		id_related = related["id"]
		field = "cert_dna_id"
		table = CertificateDna.__tablename__
		type_related = "Certificati DNA"
		view_related = DNA_HISTORY_FOR

	# Estraggo la storia delle modifiche del record di origine
	history_list = EventDB.query.filter(getattr(EventDB, field) == int(id_related), EventDB.id != int(_id)).all()
	history_list = [history.to_dict() for history in history_list]
	# print("HISTORY:", json.dumps(history_list, indent=2), "TYPE:", type(_event))
	# print("DATA:", json.dumps(_event, indent=2), "TYPE:", type(_event))

	_event = json.loads(json.dumps(_event))
	# print("EVENT:", json.dumps(_event, indent=2))

	db.session.close()
	return render_template(
		HISTORY_HTML, form=_event, restore=RESTORE_FOR, table=table,
		history_list=history_list, h_len=len(history_list), view=HISTORY_FOR,
		id_related=id_related, view_related=view_related, type_related=type_related
	)


@app.route(RESTORE, methods=["GET", "POST"])
@token_admin_validate
def event_restore(_id, id_record, table, view_for):
	try:
		models = [Administrator, Buyer, Farmer, Buyer, Slaughterhouse, Head, CertificateDna, CertificateCons]
		model = next((m for m in models if m.__tablename__ == table), None)
		# print("TABLE_DB:", model, "ID:", id_record)
		if model:
			data = EventDB.query.get(_id)
			data = data.to_dict()
			data = data["event"]["Previous_data"]
			updated_at = data["updated_at"]
			data["updated_at"] = date_to_str(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")
			data.pop("id")

			# converto boolean
			for k, v in data.items():
				if v == "SI" or v == "si":
					data[k] = True
				elif v == "NO" or v == "no":
					data[k] = False
				else:
					pass

			# print("UPDATE_DATA:", json.dumps(data, indent=2), "TYPE:", type(data))
			try:
				record = model.query.get(id_record)
				# print("DATA_FROM_DB:", json.dumps(record.to_dict(), indent=2), "TYPE:", type(data))
				for k, v in data.items():
					setattr(record, k, v)
				db.session.commit()
				flash(f"Record ripristinato correttamente alla situazione precedente il: {updated_at}.")
				return redirect(url_for(view_for, _id=id_record))
			except IntegrityError as err:
				db.session.rollback()
				db.session.close()
				flash(f"ERRORE: {str(err.orig)}")
				return redirect(url_for(view_for, _id=id_record))
		else:
			return redirect(url_for(view_for, _id=id_record))
	except Exception as err:
		db.session.close()
		flash(f"ERROR: {err}")
		return redirect(url_for(view_for, _id=id_record))
