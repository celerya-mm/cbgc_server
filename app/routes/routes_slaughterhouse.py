import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db
from ..forms.form_slaughterhouse import FormSlaughterhouseCreate, FormSlaughterhouseUpdate
from ..models.slaughterhouses import Slaughterhouse
from ..utilitys.functions import event_create, token_admin_validate, str_to_date, status_si_no


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
        # print("SLAUGHT_FORM_DATA", json.dumps(form_data, indent=2))

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
            note=form_data["note"],
            # created_at=datetime.now()
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
@app.route("/slaughterhouse_view_history/<_id>", methods=["GET", "POST"])
def slaughterhouse_view_history(_id):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Interrogo il DB
    slaughterhouse = Slaughterhouse.query.filter_by(id=_id).first()
    _slaughterhouse = slaughterhouse.to_dict()

    # Estraggo la storia delle modifiche per l'utente
    history_list = slaughterhouse.events
    history_list = [history.to_dict() for history in history_list]
    return render_template(
        "slaughterhouse/slaughterhouse_view_history.html", form=_slaughterhouse, history_list=history_list)


@token_admin_validate
@app.route("/slaughterhouse_update/<_id>", methods=["GET", "POST"])
def slaughterhouse_update(_id):
    """Aggiorna dati Allevatore."""
    form = FormSlaughterhouseUpdate()
    if form.validate_on_submit():
        # recupero i dati e li converto in dict
        # form_data = json.loads(json.dumps(request.form))
        new_data = FormSlaughterhouseUpdate(request.form)
        new_data = new_data.to_db()
        # print("FORM_DATA_PASS:", json.dumps(new_data, indent=2))

        slaughterhouse = Slaughterhouse.query.get(_id)
        previous_data = slaughterhouse.to_dict()
        # print("SLAUGH_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        new_data["created_at"] = slaughterhouse.created_at
        new_data["updated_at"] = datetime.now()
        # print("SLAUGH_NEW_DATA:", json.dumps(slaughterhouse.to_dict(), indent=2))
        try:
            db.session.query(Slaughterhouse).filter_by(id=_id).update(new_data)
            db.session.commit()
            flash("MACELLO aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("slaughterhouse/slaughterhouse_update.html", form=form, id=_id)

        _event = {
            "username": session["username"],
            "Modification": f"Update Slaughterhouse whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("SLAUGH_EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, slaughterhouse_id=_id):
            return redirect(url_for('slaughterhouse_view_history', _id=_id))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('slaughterhouse_view_history', _id=_id))
    else:
        # recupero i dati del record
        slaughterhouse = Slaughterhouse.query.get(int(_id))
        # print("SLAUGHT_FIND:", slaughterhouse, type(slaughterhouse))

        form.slaughterhouse.data = slaughterhouse.slaughterhouse
        form.slaughterhouse_code.data = slaughterhouse.slaughterhouse_code

        form.email.data = slaughterhouse.email
        form.phone.data = slaughterhouse.phone

        form.address.data = slaughterhouse.address
        form.cap.data = slaughterhouse.cap
        form.city.data = slaughterhouse.city

        form.affiliation_start_date.data = str_to_date(slaughterhouse.affiliation_start_date)
        form.affiliation_end_date.data = str_to_date(slaughterhouse.affiliation_end_date)
        form.affiliation_status.data = status_si_no(slaughterhouse.affiliation_status)

        form.note_certificate.data = slaughterhouse.note_certificate
        form.note.data = slaughterhouse.note

        _info = {
            'created_at': slaughterhouse.created_at,
            'updated_at': slaughterhouse.updated_at,
        }
        # print("SLAUGHT_:", form)
        # print("SLAUGHT_FORM:", json.dumps(form.to_dict(form), indent=2))
        return render_template("slaughterhouse/slaughterhouse_update.html", form=form, id=_id, info=_info)
