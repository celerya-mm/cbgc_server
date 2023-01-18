import json

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from app.app import db

from app.models.slaughterhouses import Slaughterhouse
from app.forms.form_slaughterhouse import FormSlaughterhouseCreate, FormSlaughterhouseUpdate
from app.forms.forms import FormAffiliationChange
from app.utilitys.functions import event_create, token_admin_validate, url_to_json


@token_admin_validate
@app.route("/slaughterhouse_view/", methods=["GET", "POST"])
def slaughterhouse_view():
    """Visualizzo informazioni Allevatori."""
    # Estraggo la lista degli allevatori
    _list = Slaughterhouse.query.all()
    _list = [r.to_dict() for r in _list]
    return render_template("slaughterhouse/slaughterhouse_view.html", form=_list)


@token_admin_validate
@app.route("/slaughterhouse_create/", methods=["GET", "POST"])
def slaughterhouse_create():
    """Creazione Allevatore Consorzio."""
    form = FormSlaughterhouseCreate()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        print("SLAUGHT_FORM_DATA", json.dumps(form_data, indent=2))
        if form_data["affiliation_start_date"] is "":
            form_data["affiliation_start_date"] = None

        if form_data["affiliation_status"] == "NO":
            form_data["affiliation_status"] = False
        else:
            form_data["affiliation_status"] = True

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

            note_certificate=form_data["note_certificate"],
            note=form_data["note"]
        )
        try:
            db.session.add(new_slaughterhouse)
            db.session.commit()
            flash("MACELLO creato correttamente.")
            return redirect(url_for('slaughterhouse_view'))
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("slaughterhouse/slaughterhouse_create.html", form=form)
    else:
        return render_template("slaughterhouse/slaughterhouse_create.html", form=form)


@token_admin_validate
@app.route("/slaughterhouse_view_history/<data>", methods=["GET", "POST"])
def slaughterhouse_view_history(data):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Elaboro i dati ricevuti
    data = url_to_json(data)
    print("SLAUGHT_DATA_PASS:", json.dumps(data, indent=2))

    # Estraggo l' ID dell'allevatore corrente
    session["slaughterhouse_id"] = data["id"]

    # Interrogo il DB
    slaughterhouse = Slaughterhouse.query.filter_by(id=data["id"]).first()
    _slaughterhouse = slaughterhouse.to_dict()

    # Estraggo la storia delle modifiche per l'utente
    history_list = slaughterhouse.event
    history_list = [history.to_dict() for history in history_list]
    print("HISTORY_EVENTS:", json.dumps(history_list, indent=2))
    return render_template("slaughterhouse/slaughterhouse_view_history.html",
                           form=_slaughterhouse, history_list=history_list)


@token_admin_validate
@app.route("/slaughterhouse_update/<data>", methods=["GET", "POST"])
def slaughterhouse_update(data):
    """Aggiorna dati Allevatore."""
    form = FormSlaughterhouseUpdate()
    if form.validate_on_submit():
        # recupero i dati e li converto in dict
        form_data = json.loads(json.dumps(request.form))
        # print("FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        _id = session["slaughterhouse_id"]
        # print("SLAUGH_ID:", _id)
        slaughterhouse = Slaughterhouse.query.get(_id)
        previous_data = slaughterhouse.to_dict()
        # print("SLAUGH_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        slaughterhouse.slaughterhouse = form_data["slaughterhouse"].strip()
        slaughterhouse.farmer_name = form_data["slaughterhouse_code"].strip()

        slaughterhouse.email = form_data["email"].strip()
        slaughterhouse.phone = form_data["phone"].strip()

        slaughterhouse.address = form_data["address"].strip()
        slaughterhouse.cap = form_data["cap"].strip()
        slaughterhouse.city = form_data["city"].strip()

        if form_data["affiliation_start_date"]:
            slaughterhouse.affiliation_start_date = form_data["affiliation_start_date"]

        if form_data["note_certificate"]:
            slaughterhouse.note_certificate = form_data["note_certificate"].strip()
        if form_data["note"]:
            slaughterhouse.note = form_data["note"].strip()

        print("SLAUGH_NEW_DATA:", json.dumps(slaughterhouse.to_dict(), indent=2))

        try:
            db.session.commit()
            flash("MACELLO aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("slaughterhouse/slaughterhouse_update.html", form=form)

        _event = {
            "username": session["username"],
            "Modification": f"Update Slaughterhouse whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("SLAUGH_EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, slaughterhouse_id=_id):
            return redirect(url_for('slaughterhouse_view_history', data=slaughterhouse.to_dict()))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('slaughterhouse_view'))
    else:
        # recupero i dati e li converto in dict
        data = url_to_json(data)
        # print("FARM_DATA_PASS:", json.dumps(data, indent=2))

        session["slaughterhouse_id"] = data["id"]

        form.slaughterhouse.data = data["slaughterhouse"]
        form.slaughterhouse_code.data = data["slaughterhouse_code"]
        
        form.email.data = data["email"]
        form.phone.data = data["phone"]

        form.address.data = data["address"]
        form.cap.data = data["cap"]
        form.city.data = data["city"]

        if "note_certificate" in data.keys() and data["note_certificate"] not in ["", None]:
            form.note_certificate.data = data["note_certificate"]

        form.note.data = data["note"]

        status = data["affiliation_status"]
        return render_template("slaughterhouse/slaughterhouse_update.html", form=form, status=status, id=data["id"])


@token_admin_validate
@app.route("/slaughterhouse_affiliation_change/<data>", methods=["GET", "POST"])
def slaughterhouse_affiliation_change(data):
    """Aggiorna dati Allevatore."""
    form = FormAffiliationChange()
    if form.validate_on_submit():
        # recupero i dati e li converto in dict
        form_data = json.loads(json.dumps(request.form))
        # print("SLAGH_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        slaughterhouse = Slaughterhouse.query.filter_by(slaughterhouse=session["slaughterhouse"]).first()
        previous_data = slaughterhouse.to_dict()
        # print("SLAGH_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        if form_data["affiliation_status"] in ["SI", True]:
            slaughterhouse.affiliation_status = True
        else:
            slaughterhouse.affiliation_status = False

        slaughterhouse.affiliation_start_date = form_data["affiliation_start_date"]
        slaughterhouse.affiliation_end_date = form_data["affiliation_end_date"]

        print("SLAGH_NEW_DATA:", json.dumps(slaughterhouse.to_dict(), indent=2))

        try:
            db.session.commit()
            flash("MACELLO aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template(
                "slaughterhouse/slaughterhouse_affiliation_change.html", form=slaughterhouse.to_dict())

        _event = {
            "username": session["username"],
            "Modification": f"Update Macello whit id: {slaughterhouse.id}",
            "Previous_data": previous_data
        }
        # print("EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, slaughterhouse_id=slaughterhouse.id):
            return redirect(url_for('slaughterhouse_view_history', data=slaughterhouse.to_dict()))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('slaughterhouse_view'))
    else:
        # recupero i dati e li converto in dict
        print("FARM_DATA_FROM_HTML:", data, "TYPE:", type(data))

        # data = data.to_dict()
        val_date = {
            1: "affiliation_start_date",
            2: "affiliation_end_date"
        }
        data = url_to_json(data, val_date)
        print("FARM_DATA_PASS_DICT:", json.dumps(data, indent=2))

        form.name.data = data["slaughterhouse"]
        form.affiliation_start_date.data = data["affiliation_start_date"]
        form.affiliation_end_date.data = data["affiliation_start_date"]
        session["slaughterhouse"] = data["slaughterhouse"]
        return render_template(
            "slaughterhouse/slaughterhouse_affiliation_change.html", form=form, id=session["slaughterhouse_id"])
