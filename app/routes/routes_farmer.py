import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from app.app import db
from app.forms.form_farmer import FormFarmerCreate, FormFarmerUpdate
from app.forms.forms import FormAffiliationChange
from app.models.farmers import Farmer
from app.utilitys.functions import event_create, token_admin_validate, url_to_json


@token_admin_validate
@app.route("/farmer_view/", methods=["GET", "POST"])
def farmer_view():
    """Visualizzo informazioni Allevatori."""
    # Estraggo la lista degli allevatori
    _list = Farmer.query.all()
    _list = [r.to_dict() for r in _list]
    return render_template("farmer/farmer_view.html", form=_list)


@token_admin_validate
@app.route("/farmer_create/", methods=["GET", "POST"])
def farmer_create():
    """Creazione Allevatore Consorzio."""
    form = FormFarmerCreate()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        # print("FARMER_FORM_DATA", json.dumps(form_data, indent=2))
        if form_data["affiliation_status"] == "NO":
            form_data["affiliation_status"] = False
        else:
            form_data["affiliation_status"] = True

        new_farmer = Farmer(
            farmer_name=form_data["farmer_name"].strip(),

            email=form_data["email"].strip(),
            phone=form_data["phone"].strip(),

            address=form_data["address"].strip(),
            cap=form_data["cap"].strip(),
            city=form_data["city"].strip(),

            affiliation_start_date=form_data["affiliation_start_date"],
            affiliation_status=form_data["affiliation_status"],

            stable_code=form_data["stable_code"],
            stable_type=form_data["stable_type"],
            stable_productive_orientation=form_data["stable_productive_orientation"],
            stable_breeding_methods=form_data["stable_breeding_methods"],

            note_certificate=form_data["note_certificate"],
            note=form_data["note"]
        )
        try:
            db.session.add(new_farmer)
            db.session.commit()
            flash("ALLEVATORE creato correttamente.")
            return redirect(url_for('farmer_view'))
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("farmer/farmer_create.html", form=form)
    else:
        return render_template("farmer/farmer_create.html", form=form)


@token_admin_validate
@app.route("/farmer_view_history/<data>", methods=["GET", "POST"])
def farmer_view_history(data):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Elaboro i dati ricevuti
    data = url_to_json(data)
    # print("FARMER_DATA_PASS:", json.dumps(data, indent=2))

    # Estraggo l' ID dell'allevatore corrente
    session["id_farmer"] = data["id"]

    # Interrogo il DB
    farmer = Farmer.query.filter_by(id=data["id"]).first()
    _farmer = farmer.to_dict()
    session["user"] = _farmer

    # Estraggo la storia delle modifiche per l'utente
    history_list = farmer.events
    history_list = [history.to_dict() for history in history_list]
    return render_template("farmer/farmer_view_history.html", form=_farmer, history_list=history_list)


@token_admin_validate
@app.route("/farmer_update/<data>", methods=["GET", "POST"])
def farmer_update(data):
    """Aggiorna dati Allevatore."""
    form = FormFarmerUpdate()
    if form.validate_on_submit():
        # recupero i dati e li converto in dict
        form_data = json.loads(json.dumps(request.form))
        # print("FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        _id = session["id_farmer"]
        # print("USER_ID:", _id)
        farmer = Farmer.query.get(_id)
        previous_data = farmer.to_dict()
        # print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        farmer.farmer_name = form_data["farmer_name"].strip()

        farmer.email = form_data["email"].strip()
        farmer.phone = form_data["phone"].strip()

        farmer.address = form_data["address"].strip()
        farmer.cap = form_data["cap"].strip()
        farmer.city = form_data["city"].strip()

        if form_data["affiliation_start_date"]:
            farmer.affiliation_start_date = form_data["affiliation_start_date"]

        farmer.stable_code = form_data["stable_code"].strip()
        farmer.stable_type = form_data["stable_type"].strip()
        farmer.stable_productive_orientation = form_data["stable_productive_orientation"].strip()
        farmer.stable_breeding_methods = form_data["stable_breeding_methods"].strip()

        if form_data["note_certificate"]:
            farmer.note_certificate = form_data["note_certificate"].strip()
        if form_data["note"]:
            farmer.note = form_data["note"].strip()

        # print("FARM_NEW_DATA:", json.dumps(farmer.to_dict(), indent=2))

        try:
            db.session.commit()
            flash("ALLEVATORE aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("farmer/farmer_update.html", form=form)

        _event = {
            "username": session["username"],
            "Modification": f"Update Farmer whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, farmer_id=_id):
            return redirect(url_for('farmer_view_history', data=farmer.to_dict()))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('farmer_view'))
    else:
        # recupero i dati e li converto in dict
        data = url_to_json(data)
        # print("FARM_DATA_PASS:", json.dumps(data, indent=2))

        session["id_farmer"] = data["id"]

        form.farmer_name.data = data["farmer_name"]
        form.email.data = data["email"]
        form.phone.data = data["phone"]

        form.address.data = data["address"]
        form.cap.data = data["cap"]
        form.city.data = data["city"]

        form.stable_code.data = data["stable_code"]
        form.stable_type.data = data["stable_type"]

        form.stable_productive_orientation.data = data["stable_productive_orientation"]
        form.stable_breeding_methods.data = data["stable_breeding_methods"]

        if "affiliation_start_date" in data.keys() and data["affiliation_start_date"] not in ["", None]:
            form.affiliation_start_date.data = datetime.strptime(data["affiliation_start_date"], '%Y-%m-%d')

        if "note_certificate" in data.keys() and data["note_certificate"] not in ["", None]:
            form.note_certificate.data = data["note_certificate"]

        form.note.data = data["note"]

        status = data["affiliation_status"]

        if data["affiliation_end_date"]:
            end_date = data["affiliation_end_date"]
        else:
            end_date = "vuoto"

        return render_template("farmer/farmer_update.html", form=form, status=status, end_date=end_date)


@token_admin_validate
@app.route("/farmer_affiliation_change/<data>", methods=["GET", "POST"])
def farmer_affiliation_change(data):
    """Aggiorna dati Allevatore."""
    form = FormAffiliationChange()
    if form.validate_on_submit():
        # recupero i dati e li converto in dict
        form_data = json.loads(json.dumps(request.form))
        # print("FARM_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        farmer = Farmer.query.filter_by(farmer_name=session["farmer_name"]).first()
        previous_data = farmer.to_dict()
        # print("FARM_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        if form_data["affiliation_status"] in ["SI", True]:
            farmer.affiliation_status = True
        else:
            farmer.affiliation_status = False

        farmer.affiliation_start_date = form_data["affiliation_start_date"]
        farmer.affiliation_end_date = form_data["affiliation_end_date"]

        print("FARM_NEW_DATA:", json.dumps(farmer.to_dict(), indent=2))

        try:
            db.session.commit()
            flash("ALLEVATORE aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("farmer/farmer_affiliation_change.html", form=farmer.to_dict())

        _event = {
            "username": session["username"],
            "Modification": f"Update Farmer whit id: {farmer.id}",
            "Previous_data": previous_data
        }
        # print("EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, farmer_id=farmer.id):
            return redirect(url_for('farmer_view_history', data=farmer.to_dict()))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('farmer_view'))
    else:
        data = url_to_json(data)
        # print("FARM_DATA_PASS_DICT:", json.dumps(data, indent=2))

        form.name.data = data["farmer_name"]
        session["farmer_name"] = data["farmer_name"]

        return render_template("farmer/farmer_affiliation_change.html", form=form)
