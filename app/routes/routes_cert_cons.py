import json

from flask import current_app as app, flash, redirect, render_template, url_for, request, send_file
from sqlalchemy.exc import IntegrityError

from ..app import db, session, Config
from ..forms.form_cert_cons import FormCertConsCreate, FormCertConsUpdate
from ..models.buyers import Buyer
from ..models.certificates_cons import CertificateCons, mount_code, year_cert_calc_update
from ..models.farmers import Farmer
from ..models.heads import Head
from ..models.slaughterhouses import Slaughterhouse
from ..utilitys.functions import (not_empty, token_admin_validate, str_to_date, calc_age,
                                  status_true_false, status_si_no, date_to_str, dict_group_by)
from ..utilitys.functions_certificates import generate_qr_code, byte_to_pdf, html_to_pdf, pdf_to_byte

VIEW = "/cert_cons/view/"
VIEW_FOR = "cert_cons_view"
VIEW_HTML = "cert_cons/cert_cons_view.html"

CREATE = "/cert_cons/create/<h_id>/<f_id>/<h_set>/"
CREATE_FOR = "cert_cons_create"
CREATE_HTML = "cert_cons/cert_cons_create.html"

HISTORY = "/cert_cons/view/history/<_id>"
HISTORY_FOR = "cert_cons_view_history"
HISTORY_HTML = "cert_cons/cert_cons_view_history.html"

UPDATE = "/cert_cons/update/<_id>"
UPDATE_FOR = "cert_cons_update"
UPDATE_HTML = "cert_cons/cert_cons_update.html"

GENERATE = "/cert_cons/generate/<_id>"
GENERATE_FOR = "cert_cons_generate"

DOWNLOAD = "/cert_cons/download/<_id>"
DOWNLOAD_FOR = "cert_cons_download"

DOWNLOAD_LINK = "/cert_cons/download_link/<_link>/"
DOWNLOAD_LINK_FOR = "cert_cons_download_link"
DOWNLOAD_LINK_HTML = "cert_cons/cert_cons_download_link.html"

SAVE = "/cert_cons/save/<_link>/"
SAVE_FOR = "cert_cons_download_save"


@app.route(VIEW, methods=["GET", "POST"])
@token_admin_validate
def cert_cons_view():
	"""Visualizzo informazioni Capi."""
	from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY
	from ..routes.routes_farmer import HISTORY_FOR as FARMER_HISTORY
	from ..routes.routes_buyer import HISTORY_FOR as BUYER_HISTORY
	from ..routes.routes_slaughterhouse import HISTORY_FOR as SLAUG_HISTORY

	_list = CertificateCons.query.all()
	_list = [r.to_dict() for r in _list]

	# raggruppa per anno del certificato
	group_year = dict_group_by(_list, "certificate_year", year=True)
	years_labels = [sub["certificate_year"] for sub in group_year]
	years_values = [sub['number'] for sub in group_year]

	# raggruppa per allevatore
	group_farmer = dict_group_by(_list, "farmer_id")
	farmers_labels = [sub["farmer_id"] for sub in group_farmer]
	farmers_values = [sub['number'] for sub in group_farmer]

	# raggruppa per acquirente
	group_buyer = dict_group_by(_list, "buyer_id")
	buyers_labels = [sub["buyer_id"] for sub in group_buyer]
	buyers_values = [sub["number"] for sub in group_buyer]

	return render_template(
		VIEW_HTML, form=_list, history=HISTORY_FOR, h_hist=HEAD_HISTORY, f_hist=FARMER_HISTORY,
		b_hist=BUYER_HISTORY, s_hist=SLAUG_HISTORY,
		years_labels=json.dumps(years_labels), years_values=json.dumps(years_values),
		farmers_labels=json.dumps(farmers_labels), farmers_values=json.dumps(farmers_values),
		buyers_labels=json.dumps(buyers_labels), buyers_values=json.dumps(buyers_values)
	)


@app.route(CREATE, methods=["GET", "POST"])
@token_admin_validate
def cert_cons_create(h_id, f_id, h_set):
	"""Creazione Certificato Consorzio."""
	from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY

	form = FormCertConsCreate()
	if form.validate_on_submit():
		form_data = json.loads(json.dumps(request.form))
		# print("HEAD_FORM_DATA", json.dumps(form_data, indent=2))

		head = Head.query.get(int(h_id))
		head_birth = head.birth_date
		head_slaug = head.slaughter_date

		new_cert = CertificateCons(
			certificate_id=form_data["certificate_id"],
			certificate_var=form_data["certificate_var"],
			certificate_date=form_data["certificate_date"],
			emitted=form_data["emitted"],

			cockade_id=form_data["cockade_id"],
			cockade_var=form_data["cockade_var"],

			sale_type=form_data["sale_type"],
			sale_quantity=form_data["sale_quantity"],
			batch_number=form_data["batch_number"],

			head_category=form_data["head_category"],
			head_age=calc_age(head_birth, head_slaug),

			invoice_nr=form_data["invoice_nr"],
			invoice_date=form_data["invoice_date"],
			invoice_status=form_data["invoice_status"],

			head_id=int(form_data["head_id"].split(" - ")[0]),
			farmer_id=int(form_data["farmer_id"].split(" - ")[0]),
			buyer_id=int(form_data["buyer_id"].split(" - ")[0]),
			slaughterhouse_id=int(form_data["slaughterhouse_id"].split(" - ")[0]),

			note_certificate=form_data["note_certificate"],
			note=form_data["note"].strip()
		)
		print("CERT_NEW_DATA", json.dumps(new_cert.to_dict(), indent=2))
		try:
			db.session.add(new_cert)
			db.session.commit()
			db.session.close()
			flash("CERTIFICATO CONSORZIO creato correttamente.")
			return redirect(url_for(HEAD_HISTORY, _id=h_id))
		except IntegrityError as err:
			db.session.rollback()
			db.session.close()
			flash(f"ERRORE: {str(err.orig)}")
			return render_template(CREATE_HTML, form=form, view=VIEW_FOR)
	else:
		max_id = db.session.query(db.func.max(CertificateCons.id)).scalar()
		prev_cert = CertificateCons.query.get(max_id)
		prev_cert = prev_cert.certificate_nr

		head = Head.query.get(int(h_id))
		head_birth = head.birth_date
		head_slaug = head.slaughter_date
		db.session.close()

		# print("HEAD", h_set, "LAST:", prev_cert)
		h_set = f"{int(h_id)} - {h_set}"
		# print("HEAD", h_set)

		form.head_id.data = h_set
		form.farmer_id.data = f_id
		form.head_age.data = calc_age(head_birth, head_slaug)

		return render_template(CREATE_HTML, form=form, view=HEAD_HISTORY, _id=h_id, h_set=h_set, prev_cert=prev_cert)


@app.route(HISTORY, methods=["GET", "POST"])
@token_admin_validate
def cert_cons_view_history(_id):
	"""Visualizzo la storia delle modifiche al record del Certificato."""
	from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY
	from ..routes.routes_farmer import HISTORY_FOR as FARMER_HISTORY
	from ..routes.routes_buyer import HISTORY_FOR as BUYER_HISTORY
	from ..routes.routes_slaughterhouse import HISTORY_FOR as SLAUG_HISTORY
	from ..routes.routes_event import HISTORY_FOR as EVENT_HISTORY

	cert = CertificateCons.query.get(int(_id))
	_cert = cert.to_dict()
	# print("HEAD_FORM:", json.dumps(_head, indent=2), "TYPE:", type(_head))

	if cert.head_id:
		head = Head.query.get(cert.head_id)
		_cert["head_id"] = f"{head.id} - {head.headset}"

	if cert.farmer_id:
		farmer = Farmer.query.get(cert.farmer_id)
		_cert["farmer_id"] = f"{farmer.id} - {farmer.farmer_name}"

	if cert.buyer_id:
		buyer = Buyer.query.get(cert.buyer_id)
		_cert["buyer_id"] = f"{buyer.id} - {buyer.buyer_name}"

	if cert.slaughterhouse_id:
		slaugh = Slaughterhouse.query.get(cert.slaughterhouse_id)  # noqa
		_cert["slaughterhouse_id"] = f"{slaugh.id} - {slaugh.slaughterhouse}"

	# Estraggo la storia delle modifiche per l'utente
	history_list = cert.events
	history_list = [history.to_dict() for history in history_list]

	_cert["emitted"] = status_si_no(_cert["emitted"])
	db.session.close()

	# print("CERT_DATA:", json.dumps(cert.to_dict(), indent=2))
	return render_template(
		HISTORY_HTML, form=_cert, history_list=history_list, h_len=len(history_list), view=VIEW_FOR,
		update=UPDATE_FOR, event_history=EVENT_HISTORY, generate=GENERATE_FOR, download=DOWNLOAD_FOR,
		head_history=HEAD_HISTORY, h_id=cert.head_id,
		farmer_history=FARMER_HISTORY, f_id=cert.farmer_id,
		buyer_history=BUYER_HISTORY, b_id=cert.buyer_id,
		slaug_history=SLAUG_HISTORY, s_id=cert.slaughterhouse_id
	)


@app.route(UPDATE, methods=["GET", "POST"])
@token_admin_validate
def cert_cons_update(_id):
	"""Aggiorna dati Capo."""
	from ..routes.routes_event import event_create

	form = FormCertConsUpdate()
	if form.validate_on_submit():
		try:
			new_data = json.loads(json.dumps(request.form))
			new_data.pop('csrf_token', None)
			# print("HEAD_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

			cert = CertificateCons.query.get(int(_id))
			previous_data = cert.to_dict()
			previous_data.pop("updated_at")
			# print("HEAD_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

			new_data["certificate_nr"] = mount_code(
				new_data["certificate_id"], new_data["certificate_year"], new_data["certificate_var"])
			new_data["certificate_date"] = str_to_date(new_data["certificate_date"])

			new_data["emitted"] = status_true_false(new_data["emitted"])

			new_data["cockade_id"] = not_empty(new_data["cockade_id"])
			new_data["cockade_nr"] = mount_code(
				new_data["cockade_id"], new_data["certificate_year"], new_data["cockade_var"])

			new_data["sale_type"] = not_empty(new_data["sale_type"])
			new_data["sale_quantity"] = not_empty(new_data["sale_quantity"])
			new_data["sale_rest"] = not_empty(new_data["sale_rest"])

			new_data["head_category"] = not_empty(new_data["head_category"])
			if new_data["head_age"] in ["", None, 0]:
				head = Head.query.get(int(cert.head_id))
				birth = head.birth_date
				slaug = head.slaughter_date
				new_data["head_age"] = calc_age(birth, slaug)
			else:
				new_data["head_age"] = not_empty(new_data["head_age"])

			new_data["batch_number"] = not_empty(new_data["batch_number"])

			new_data["invoice_nr"] = not_empty(new_data["invoice_nr"])
			new_data["invoice_date"] = str_to_date(new_data["invoice_date"])

			new_data["note_certificate"] = not_empty(new_data["note_certificate"])
			new_data["note"] = not_empty(new_data["note"])

			if new_data["head_id"] not in ["", "-", None]:
				new_data["head_id"] = int(new_data["head_id"].split(" - ")[0])
			else:
				new_data["head_id"] = None

			if new_data["buyer_id"] not in ["", "-", None]:
				new_data["buyer_id"] = int(new_data["buyer_id"].split(" - ")[0])
			else:
				new_data["buyer_id"] = None

			if new_data["farmer_id"] not in ["", "-", None]:
				new_data["farmer_id"] = int(new_data["farmer_id"].split(" - ")[0])
			else:
				new_data["farmer_id"] = None

			if new_data["slaughterhouse_id"] not in ["", "-", None]:
				new_data["slaughterhouse_id"] = int(new_data["slaughterhouse_id"].split(" - ")[0])
			else:
				new_data["slaughterhouse_id"] = None

			new_data["created_at"] = cert.created_at

			# print("CERT_NEW_DATA:", new_data)
			try:
				db.session.query(CertificateCons).filter_by(id=_id).update(new_data)
				db.session.commit()
				db.session.close()
				flash("CERTIFICATO CONSORZIO aggiornato correttamente.")

			except IntegrityError as err:
				db.session.rollback()
				db.session.close()
				flash(f"ERRORE: {str(err.orig)}")
				prev_cert = CertificateCons.query.get(int(_id) - 1)
				_info = {
					'created_at': cert.created_at,
					'updated_at': cert.updated_at,
				}
				return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR,
				                       prev_cert=prev_cert.certificate_nr)

			_event = {
				"username": session["username"],
				"table": CertificateCons.__tablename__,
				"Modification": f"Update Certificate whit id: {_id}",
				"Previous_data": previous_data
			}
			# print("EVENT:", json.dumps(_event, indent=2))
			_event = event_create(_event, cert_cons_id=int(_id))
			if _event is True:
				return redirect(url_for(HISTORY_FOR, _id=int(_id)))
			else:
				flash(_event)
				return redirect(url_for(HISTORY_FOR, _id=_id))
		except Exception as err:
			flash(err)
			return redirect(url_for(HISTORY_FOR, _id=_id))
	else:
		# recupero i dati del record
		cert = CertificateCons.query.get(int(_id))
		# recupero il record precedente
		max_id = db.session.query(db.func.max(CertificateCons.id)).scalar()
		prev_cert = CertificateCons.query.get(max_id)
		prev_cert = prev_cert.certificate_nr

		# print("HEAD_FIND:", head, type(data))

		form.certificate_id.data = cert.certificate_id
		form.certificate_var.data = cert.certificate_var
		form.certificate_date.data = str_to_date(cert.certificate_date)
		form.certificate_year.data = year_cert_calc_update(cert.certificate_date)

		form.emitted.data = status_si_no(cert.emitted)

		form.cockade_id.data = cert.cockade_id
		form.cockade_var.data = cert.cockade_var

		form.sale_type.data = cert.sale_type
		form.sale_quantity.data = cert.sale_quantity
		form.sale_rest.data = cert.sale_rest

		form.head_category.data = cert.invoice_nr
		if cert.head_age in ["", None, 0]:
			head = Head.query.get(int(cert.head_id))
			birth = head.birth_date
			slaug = head.slaughter_date
			form.head_age.data = calc_age(birth, slaug)
		else:
			form.head_age.data = cert.head_age

		form.batch_number.data = cert.batch_number

		form.invoice_nr.data = cert.invoice_nr
		form.invoice_date.data = str_to_date(cert.invoice_date)
		form.invoice_status.data = cert.invoice_status

		head = Head.query.get(cert.head_id)
		form.head_id.data = f"{head.id} - {head.headset}"

		farmer = Farmer.query.get(cert.farmer_id)
		form.farmer_id.data = f"{farmer.id} - {farmer.farmer_name}"

		buyer = Buyer.query.get(cert.buyer_id)
		form.buyer_id.data = f"{buyer.id} - {buyer.buyer_name}"

		if cert.slaughterhouse_id:
			slaugh = Slaughterhouse.query.get(cert.slaughterhouse_id)  # noqa
			form.slaughterhouse_id.data = f"{slaugh.id} - {slaugh.slaughterhouse}"

		form.note_certificate.data = cert.note_certificate
		form.note.data = cert.note

		db.session.close()

		_info = {
			'created_at': cert.created_at,
			'updated_at': cert.updated_at,
		}
		# print("CERT_:", form)
		# print("CERT_FORM:", form.to_dict())
		return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR,
		                       prev_cert=prev_cert)


@app.route(GENERATE, methods=["GET", "POST"])
@token_admin_validate
def cert_cons_generate(_id):
	"""Stampa il certificato in .pdf e carica come byte nel DB."""
	from ..routes.routes_event import event_create

	cert = CertificateCons.query.get(int(_id))
	# genero QR-Code
	# str_qr = f"109-CERT-{cert.certificate_nr}"
	nr_cert = cert.certificate_nr.replace("/", "_")
	str_qr = f"{Config.LINK_URL}:62233/cert_cons/download_link/{nr_cert}"
	print("LINK_CERTIFICATO:", str_qr)

	img_qrc = generate_qr_code(str_qr, nr_cert)
	if img_qrc:
		previous_data = cert.to_dict()  # salvo dati per creare evento record.
		previous_data.pop("updated_at")

		cert.emitted = True

		if cert.head_age in ["", None]:
			db.session.close()
			flash("Manca l'età del capo.")
			return redirect(url_for(HISTORY_FOR, _id=_id))
		elif cert.slaughterhouse_id in ["", None]:
			db.session.close()
			flash("Non hai inserito il Macello.")
			return redirect(url_for(HISTORY_FOR, _id=_id))

		try:
			# recupera dati records relazionati
			head = Head.query.get(cert.head_id)
			farmer = Farmer.query.get(cert.farmer_id)
			buyer = Buyer.query.get(cert.buyer_id)
			slaught = Slaughterhouse.query.get(cert.slaughterhouse_id)  # noqa
		except Exception as err:
			db.session.close()
			flash(f"ERRORE: {err}")
			return redirect(url_for(HISTORY_FOR, _id=_id))

		if cert.note_certificate in ["", None]:
			note = ""
		else:
			note = cert.note_certificate

		data = {
			"certificate_nr": cert.certificate_nr,
			"certificate_date": date_to_str(cert.certificate_date, '%d-%m-%Y'),
			"head_category": cert.head_category,
			"age_month": cert.head_age,
			"batch_number": cert.batch_number,
			"headset": head.headset,
			"farmer_name": farmer.farmer_name,
			"slaughter_name": slaught.slaughterhouse,
			"buyer_name": buyer.buyer_name,
			"sale_type": cert.sale_type,
			"note_cert": note
		}

		# creo un pdf del certificato
		if buyer.buyer_type and buyer.buyer_type == "Macelleria":
			pdf = html_to_pdf("cert_cons/macellerie.html", data, img_qrc)
		elif buyer.buyer_type and buyer.buyer_type == "Ristorante":
			pdf = html_to_pdf("cert_cons/restaurants.html", data, img_qrc)
		else:
			flash(f"L'acquirente non ha il tipo specificato: Ristorante o Macelleria.")
			return redirect(url_for(HISTORY_FOR, _id=_id))

		if pdf is not False:
			pdf_str = pdf_to_byte(pdf)
		else:
			flash(f"Errore creazione certificato pdf.")
			return redirect(url_for(HISTORY_FOR, _id=_id))

		# print("BUYER_TYPE:", buyer.buyer_type)
		if pdf_str is not False and pdf_str is not None and len(pdf_str) > 10:
			# assegno stringa in byte
			cert.certificate_pdf = pdf_str
			cert.emitted = True
			try:
				# db.session.query(CertificateCons).filter_by(id=cert.id).update(cert)
				db.session.commit()
				flash("CERTIFICATO CREATO correttamente.")
				previous_data["certificate_pdf"] = "Campo troppo lungo, rimosso i dati." \
				                                   "Conterrebbe il certificato pdf convertito in byte."
			except IntegrityError as err:
				db.session.rollback()
				db.session.close()
				flash(f"ERRORE: {str(err.orig)}")
				return redirect(url_for(HISTORY_FOR, _id=_id))

			_event = {
				"username": session["username"],
				"table": CertificateCons.__tablename__,
				"Modification": f"Update Certificate whit id: {_id}",
				"Previous_data": previous_data
			}
			# print("EVENT:", json.dumps(_event, indent=2))
			_event = event_create(_event, cert_cons_id=int(_id))
			if _event is True:
				return redirect(url_for(HISTORY_FOR, _id=int(_id)))
			else:
				flash(_event)
				return redirect(url_for(HISTORY_FOR, _id=int(_id)))
		else:
			flash(f"ERRORE CREAZIONE PDF.")
			db.session.close()
			return redirect(url_for(HISTORY_FOR, _id=_id))
	else:
		flash(f"ERRORE CREAZIONE PDF.")
		db.session.close()
		return redirect(url_for(HISTORY_FOR, _id=_id))


@app.route(DOWNLOAD, methods=["GET", "POST"])
@token_admin_validate
def cert_cons_download(_id):
	cert = CertificateCons.query.get(int(_id))
	if cert.certificate_pdf and len(cert.certificate_pdf) > 100:
		_pdf = byte_to_pdf(cert.certificate_pdf, cert.certificate_nr)
		return send_file(_pdf, as_attachment=True)
	else:
		return redirect(url_for(HISTORY_FOR, _id=_id))


@app.route(DOWNLOAD_LINK, methods=["GET", "POST"])
def cert_cons_download_link(_link):
	return render_template(DOWNLOAD_LINK_HTML, cert_nr=_link, func=SAVE_FOR)


@app.route(SAVE, methods=["GET", "POST"])
def cert_cons_download_save(_link):
	_link = _link.replace("_", "/")
	try:
		cert = db.session.query(CertificateCons).filter_by(certificate_nr=_link).first()
		print("LINK", _link)
		_pdf = byte_to_pdf(cert.certificate_pdf, cert.certificate_nr)
		print("PDF_GENERATO")
		flash(f"Certificato Consorzio Bue Grasso di Carrù nr {_link} scaricato.")
		return send_file(_pdf, as_attachment=True)
	except Exception as err:
		print("PDF_NON_GENERATO:", err)
		_link = _link.replace("/", "_")
		flash(f"Certificato Consorzio Bue Grasso di Carrù nr {_link} non trovato.")
		return render_template(DOWNLOAD_LINK_HTML, cert_nr=_link, func=SAVE_FOR)
