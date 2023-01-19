import json

from flask import current_app as app, flash, redirect, render_template, url_for, request, session
from sqlalchemy.exc import IntegrityError

from ..app import db
from ..forms.form_buyer import FormBuyerCreate, FormBuyerUpdate
from ..models.accounts import User
from ..models.buyers import Buyer
from ..utilitys.functions import token_admin_validate, event_create, url_to_json, affiliation_status


def find_user_id(_id):
    """Cerca l'utente nel DB e ritorna l'ID."""
    if _id not in ["", "-", None]:
        user_search = _id.split(" - ")[0]
        user_id = User.query.filter_by(username=user_search).first()
        return user_id.id
    else:
        return None


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
        new_farmer = Buyer(
            buyer_name=form_data["buyer_name"].strip(),
            buyer_type=form_data["buyer_type"].strip(),

            email=form_data["email"].strip(),
            phone=form_data["phone"].strip(),

            address=form_data["address"].strip(),
            cap=form_data["cap"].strip(),
            city=form_data["city"].strip(),

            affiliation_start_date=form_data["affiliation_start_date"],
            affiliation_status=affiliation_status(form_data["affiliation_status"]),

            user_id=find_user_id(form_data["user_id"]),

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
    if buyer.user_id not in ["", None]:
        user = User.query.get(buyer.user_id)
        _buyer["user_full"] = f"ID = {buyer.user_id}; Username =  {user.username}; Nome Completo = {user.full_name}"
        # print("BUYER_VIEW_DATA:", json.dumps(_buyer, indent=2), "TYPE:", type(_buyer))

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

        buyer.affiliation_start_date = form_data["affiliation_start_date"]
        buyer.affiliation_end_date = form_data["affiliation_end_date"]
        buyer.affiliation_status = form_data["affiliation_status"]

        buyer.note_certificate = form_data["note_certificate"].strip()
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

        form.affiliation_start_date.data = data["affiliation_start_date"]
        form.affiliation_end_date.data = data["affiliation_end_date"]
        form.affiliation_status.data = data["affiliation_status"]

        if "note_certificate" in data.keys() and data["note_certificate"] not in ["", None]:
            form.note_certificate.data = data["note_certificate"]

        form.note.data = data["note"]

        status = data["affiliation_status"]
        return render_template("buyer/buyer_update.html", form=form, status=status, id=data["id"])
