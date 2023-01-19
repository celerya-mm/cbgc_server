import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, url_for, request, session
from sqlalchemy.exc import IntegrityError

from app.app import db
from app.forms.form_buyer import FormBuyerCreate, FormBuyerUpdate
from app.forms.forms import FormAffiliationChange
from app.models.accounts import User
from app.models.buyers import Buyer
from app.utilitys.functions import token_admin_validate, event_create, url_to_json


@token_admin_validate
@app.route("/buyer_view/", methods=["GET", "POST"])
def buyer_view():
    """Visualizza informazioni Acquirenti."""
    # Estraggo la lista degli allevatori
    _list = Buyer.query.all()
    _list = [r.to_dict() for r in _list]
    return render_template("buyer/buyer_view.html", form=_list)


@token_admin_validate
@app.route("/buyer_create/", methods=["GET", "POST"])
def buyer_create():
    """Creazione Allevatore Consorzio."""
    form = FormBuyerCreate()
    if form.validate_on_submit():
        # print("SECRET:", secret)
        form_data = json.loads(json.dumps(request.form))
        # print("BUYER_FORM_DATA", json.dumps(form_data, indent=2))
        if form_data["affiliation_status"] == "NO":
            form_data["affiliation_status"] = False
        else:
            form_data["affiliation_status"] = True

        user_search = form_data["user_id"]
        user_search = user_search.split(" - ")[0]
        user_find = User.query.filter_by(username=user_search).first()

        # print("USER_ID:", user_find.id)

        new_farmer = Buyer(
            buyer_name=form_data["buyer_name"].strip(),
            buyer_type=form_data["buyer_type"].strip(),

            email=form_data["email"].strip(),
            phone=form_data["phone"].strip(),

            address=form_data["address"].strip(),
            cap=form_data["cap"].strip(),
            city=form_data["city"].strip(),

            affiliation_start_date=form_data["affiliation_start_date"],
            affiliation_status=form_data["affiliation_status"],

            user_id=user_find.id,

            note_certificate=form_data["note_certificate"],
            note=form_data["note"]
        )
        try:
            db.session.add(new_farmer)
            db.session.commit()
            flash("ACQUIRENTE creato correttamente.")
            return redirect(url_for('buyer_view'))
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("buyer/buyer_create.html", form=form)
    else:
        return render_template("buyer/buyer_create.html", form=form)


@token_admin_validate
@app.route("/buyer_view_history/<data>", methods=["GET", "POST"])
def buyer_view_history(data):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Elaboro i dati ricevuti
    data = url_to_json(data)
    # print("BUYER_VIEW_DATA_PASS:", json.dumps(data, indent=2))

    # Estraggo l' ID dell'allevatore corrente
    session["id_buyer"] = data["id"]

    # Interrogo il DB
    buyer = Buyer.query.filter_by(id=data["id"]).first()
    _buyer = buyer.to_dict()
    session["buyer"] = _buyer

    # Estraggo la storia delle modifiche per l'utente
    history_list = buyer.events
    history_list = [history.to_dict() for history in history_list]

    # Estraggo l'utente collegato
    try:
        user = User.query.get(buyer.user_id)
        _buyer["user_full"] = f"ID = {buyer.user_id}; Username =  {user.username}; Nome Completo = {user.full_name}"
        # print("BUYER_VIEW_DATA:", json.dumps(_buyer, indent=2), "TYPE:", type(_buyer))
    except Exception as err:
        print("ERRORE:", err)
        pass

    return render_template("buyer/buyer_view_history.html", form=_buyer, history_list=history_list)


@token_admin_validate
@app.route("/buyer_update/<data>", methods=["GET", "POST"])
def buyer_update(data):
    """Aggiorna dati Allevatore."""
    form = FormBuyerUpdate()
    if form.validate_on_submit():
        # recupero i dati e li converto in dict
        form_data = json.loads(json.dumps(request.form))
        # print("BUYER_UPDATE_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        _id = session["id_buyer"]
        # print("USER_ID:", _id)
        buyer = Buyer.query.get(_id)
        previous_data = buyer.to_dict()
        # print("BUYER_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        buyer.buyer_name = form_data["buyer_name"].strip()
        buyer.buyer_type = form_data["buyer_type"].strip()

        buyer.email = form_data["email"].strip()
        buyer.phone = form_data["phone"].strip()

        buyer.address = form_data["address"].strip()
        buyer.cap = form_data["cap"].strip()
        buyer.city = form_data["city"].strip()

        if "affiliation_start_date" in form_data.keys():
            buyer.affiliation_start_date = form_data["affiliation_start_date"]

        if "note_certificate" in form_data.keys():
            buyer.note_certificate = form_data["note_certificate"].strip()
        if "note" in form_data.keys():
            buyer.note = form_data["note"].strip()

        # print("BUYER_NEW_DATA:", json.dumps(buyer.to_dict(), indent=2))

        try:
            db.session.commit()
            flash("ACQUIRENTE aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("buyer/buyer_update.html", form=form)

        _event = {
            "username": session["username"],
            "Modification": f"Update Buyer whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("BUYER_EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, buyer_id=_id):
            return redirect(url_for('buyer_view_history', data=buyer.to_dict()))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('buyer_view'))
    else:
        # recupero i dati e li converto in dict
        data = url_to_json(data)
        # print("BUYER_UPDATE_DATA_PASS:", json.dumps(data, indent=2))

        session["id_buyer"] = data["id"]

        form.buyer_name.data = data["buyer_name"]
        form.buyer_type.data = data["buyer_type"]

        form.email.data = data["email"]
        form.phone.data = data["phone"]

        form.address.data = data["address"]
        form.cap.data = data["cap"]
        form.city.data = data["city"]

        if "affiliation_start_date" in data.keys() and data["affiliation_start_date"] not in ["", None]:
            form.affiliation_start_date.data = datetime.strptime(data["affiliation_start_date"], '%Y-%m-%d')

        if "note_certificate" in data.keys() and data["note_certificate"] not in ["", None]:
            form.note_certificate.data = data["note_certificate"]

        form.note.data = data["note"]

        status = data["affiliation_status"]

        if "affiliation_end_date" in data.keys():
            end_date = data["affiliation_end_date"]
        else:
            end_date = "vuoto"

        return render_template("buyer/buyer_update.html", form=form, status=status, end_date=end_date)


@token_admin_validate
@app.route("/buyer_affiliation_change/<data>", methods=["GET", "POST"])
def buyer_affiliation_change(data):
    """Aggiorna dati Allevatore."""
    form = FormAffiliationChange()
    if form.validate_on_submit():
        # recupero i dati e li converto in dict
        form_data = json.loads(json.dumps(request.form))
        # print("BUYER_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        farmer = Buyer.query.filter_by(buyer_name=session["buyer_name"]).first()
        previous_data = farmer.to_dict()
        # print("BUYER_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        if form_data["affiliation_status"] in ["SI", True]:
            farmer.affiliation_status = True
        else:
            farmer.affiliation_status = False

        farmer.affiliation_start_date = form_data["affiliation_start_date"]
        farmer.affiliation_end_date = form_data["affiliation_end_date"]

        # print("BUYER_NEW_DATA:", json.dumps(farmer.to_dict(), indent=2))

        try:
            db.session.commit()
            flash("ACQUIRENTE aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("buyer/buyer_affiliation_change.html", form=farmer.to_dict())

        _event = {
            "username": session["username"],
            "Modification": f"Update Buyer whit id: {farmer.id}",
            "Previous_data": previous_data
        }
        # print("EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, buyer_id=farmer.id):
            return redirect(url_for('buyer_view_history', data=farmer.to_dict()))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('farmer_view'))
    else:
        # recupero i dati e li converto in dict
        # print("BUYER_DATA_FROM_HTML:", data, "TYPE:", type(data))

        # data = data.to_dict()
        val_date = {
            1: "affiliation_start_date",
            2: "affiliation_end_date"
        }

        data = url_to_json(data, val_date)
        # print("BUYER_DATA_PASS_DICT:", json.dumps(data, indent=2))

        form.name.data = data["buyer_name"]
        session["buyer_name"] = data["buyer_name"]

        return render_template("buyer/buyer_affiliation_change.html", form=form)
