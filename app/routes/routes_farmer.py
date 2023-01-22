import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db
from ..forms.form_farmer import FormFarmerCreate, FormFarmerUpdate
from ..models.farmers import Farmer
from ..utilitys.functions import event_create, token_admin_validate, status_true_false, str_to_date, status_si_no, \
    address_mount

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


@token_admin_validate
@app.route(VIEW, methods=["GET", "POST"])
def farmer_view():
    """Visualizzo informazioni Allevatori."""
    # Estraggo la lista degli allevatori
    _list = Farmer.query.all()
    _list = [r.to_dict() for r in _list]
    return render_template(VIEW_HTML, form=_list, create=CREATE_FOR, update=UPDATE_FOR, history=HISTORY_FOR)


@token_admin_validate
@app.route(CREATE, methods=["GET", "POST"])
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

            note_certificate=form_data["note_certificate"].strip(),
            note=form_data["note"].strip()
        )
        try:
            db.session.add(new_farmer)
            db.session.commit()
            flash("ALLEVATORE creato correttamente.")
            return redirect(url_for('farmer/view'))
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template(CREATE_HTML, form=form, view=VIEW_FOR)
    else:
        return render_template(CREATE_HTML, form=form, view=VIEW_FOR)


@token_admin_validate
@app.route(HISTORY, methods=["GET", "POST"])
def farmer_view_history(_id):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Interrogo il DB
    farmer = Farmer.query.get(int(_id))
    _farmer = farmer.to_dict()

    # Estraggo la storia delle modifiche per l'utente
    history_list = farmer.events
    history_list = [history.to_dict() for history in history_list]
    len_history = len(history_list)

    # Estraggo l'elenco dei capi dell' Allevatore
    heads = farmer.heads
    heads = [head.to_dict() for head in heads]

    return render_template(HISTORY_HTML, form=_farmer, history_list=history_list, h_len=len_history, view=VIEW_FOR,
                           update=UPDATE_FOR, heads=heads)


@token_admin_validate
@app.route(UPDATE, methods=["GET", "POST"])
def farmer_update(_id):
    """Aggiorna dati Allevatore."""
    form = FormFarmerUpdate()
    if form.validate_on_submit():
        # recupero i dati e li converto in dict
        new_data = json.loads(json.dumps(request.form))
        new_data.pop('csrf_token', None)
        # print("FORM_DATA_PASS:", json.dumps(new_data, indent=2))

        farmer = Farmer.query.get(_id)
        previous_data = farmer.to_dict()
        # print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        new_data["full_address"] = address_mount(new_data["address"], new_data["cap"], new_data["city"])
        new_data["affiliation_status"] = status_true_false(new_data["affiliation_status"])

        new_data["created_at"] = farmer.created_at
        new_data["updated_at"] = datetime.now()
        print("NEW_DATA:", new_data)
        try:
            db.session.query(Farmer).filter_by(id=_id).update(new_data)
            db.session.commit()
            flash("ALLEVATORE aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            _info = {
                'created_at': farmer.created_at,
                'updated_at': farmer.updated_at,
            }
            return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)

        _event = {
            "username": session["username"],
            "Modification": f"Update Farmer whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, farmer_id=_id):
            return redirect(url_for(HISTORY_FOR, _id=_id))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
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

        form.note_certificate.data = farmer.note_certificate
        form.note.data = farmer.note

        _info = {
            'created_at': farmer.created_at,
            'updated_at': farmer.updated_at,
        }
        # print("FARMER_:", form)
        # print("FARMER_FORM:", json.dumps(form.to_dict(form), indent=2))
        return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)
