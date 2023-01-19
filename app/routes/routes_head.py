import json

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db

from ..models.heads import Head, verify_castration
from ..models.farmers import Farmer
from ..models.buyers import Buyer
from ..models.slaughterhouses import Slaughterhouse

from ..forms.form_head import FormHeadCreate, FormHeadUpdate
from ..utilitys.functions import event_create, token_admin_validate, url_to_json, str_to_date


def not_empty(_v):
    """Verifica se il dato passato è vuoto o da non considerare."""
    if _v in ["", "-", None]:
        return None
    else:
        _v = _v.strip()
        return _v


@token_admin_validate
@app.route("/head_view/", methods=["GET", "POST"])
def head_view():
    """Visualizzo informazioni Capi."""
    _list = Head.query.all()
    _list = [r.to_dict() for r in _list]
    return render_template("head/head_view.html", form=_list, dict_to_json=url_to_json)


@token_admin_validate
@app.route("/head_create/", methods=["GET", "POST"])
def head_create():
    """Creazione Capo Consorzio."""
    form = FormHeadCreate()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        # print("HEAD_FORM_DATA", json.dumps(form_data, indent=2))

        new_head = Head(
            headset=form_data["headset"],

            birth_date=not_empty(form_data["birth_date"]),
            castration_date=not_empty(form_data["castration_date"]),

            slaughter_date=not_empty(form_data["slaughter_date"]),
            sale_date=not_empty(form_data["sale_date"]),

            farmer_id=not_empty(form_data["farmer_id"]),
            buyer_id=not_empty(form_data["buyer_id"]),
            slaughterhouse_id=not_empty(form_data["slaughterhouse_id"]),

            note_certificate=form_data["note_certificate"],
            note=form_data["note"].strip(),
        )
        print("HEAD_NEW_DATA", json.dumps(new_head.to_dict(), indent=2))
        try:
            db.session.add(new_head)
            db.session.commit()
            flash("CAPO creato correttamente.")
            return redirect(url_for('head_view'))
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("head/head_create.html", form=form)
    else:
        return render_template("head/head_create.html", form=form)


@token_admin_validate
@app.route("/head_view_history/<data>", methods=["GET", "POST"])
def head_view_history(data):
    """Visualizzo la storia delle modifiche al record del Capo."""
    head = Head.query.get(int(data))
    _head = head.to_dict()
    # print("HEAD_FORM:", json.dumps(_head, indent=2), "TYPE:", type(_head))

    if head.farmer_id:
        farmer = Farmer.query.get(head.farmer_id)
        _head["farmer_id"] = f"{farmer.id} - {farmer.farmer_name}"

    if head.buyer_id:
        buyer = Buyer.query.get(head.buyer_id)
        _head["buyer_id"] = f"{buyer.id} - {buyer.buyer_name}"

    if head.slaughterhouse_id:
        slaughter = Slaughterhouse.query.get(head.slaughterhouse_id)
        _head["buyer_id"] = f"{slaughter.id} - {slaughter.slaughterhouse}"

    head.note = head.note
    head.note_certificate = head.note_certificate

    # Estraggo la storia delle modifiche per l'utente
    history_list = head.events
    history_list = [history.to_dict() for history in history_list]
    return render_template(
        "head/head_view_history.html", form=_head, history_list=history_list)


@token_admin_validate
@app.route("/head_update/<data>", methods=["GET", "POST"])
def head_update(data):
    """Aggiorna dati Capo."""
    form = FormHeadUpdate()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        # print("HEAD_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        _id = session["head_id"]
        head = Head.query.get(_id)

        previous_data = head.to_dict()
        # print("HEAD_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        head.headset = form_data["headset"]

        head.birth_date = not_empty(form_data["birth_date"])
        head.castration_date = not_empty(form_data["castration_date"])
        head.castration_compliance = verify_castration(form_data["birth_date"], form_data["castration_date"])

        head.slaughter_date = not_empty(form_data["slaughter_date"])
        head.sale_date = not_empty(form_data["sale_date"])

        if form_data["farmer_id"] in ["", "-"]:
            head.farmer_id = None
        else:
            farmer = Farmer.query.filter_by(farmer_name=form_data["farmer_id"].split(" - ")[0]).first()
            head.farmer_id = farmer.id

        if form_data["buyer_id"] in ["", "-"]:
            head.buyer_id = None
        else:
            buyer = Buyer.query.filter_by(buyer_name=form_data["buyer_id"].split(" - ")[0]).first()
            head.buyer_id = buyer.id

        if form_data["slaughterhouse_id"] in ["", "-"]:
            head.slaughterhouse_id = None
        else:
            slaughter = Slaughterhouse.query.filter_by(
                slaughterhouse=form_data["slaughterhouse_id"].split(" - ")[0]).first()
            head.slaughterhouse_id = slaughter.id

        head.note_certificate = not_empty(form_data["note_certificate"])
        head.note = not_empty(form_data["note"])

        print("HEAD_NEW_DATA:", json.dumps(head.to_dict(), indent=2))
        try:
            db.session.commit()
            flash("CAPO aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("user/user_update.html", form=form)

        _event = {
            "username": session["username"],
            "Modification": f"Update Head whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, head_id=_id):
            return redirect(url_for('head_view_history', data=_id))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('head_view_history', data=_id))
    else:
        # recupero i dati e li converto in dict
        head = Head.query.get(int(data))
        # print("HEAD_FIND:", head, type(data))

        session["head_id"] = head.id

        form.headset.data = head.headset

        form.birth_date.data = str_to_date(head.birth_date)
        form.castration_date.data = str_to_date(head.castration_date)
        form.slaughter_date.data = str_to_date(head.slaughter_date)
        form.sale_date.data = str_to_date(head.sale_date)

        if head.farmer_id and head.farmer_id not in [None, "None", ""]:
            farmer = Farmer.query.get(head.farmer_id)
            form.farmer_id.data = str(farmer.id) + " - " + farmer.farmer_name

        if head.buyer_id and head.buyer_id not in [None, "None", ""]:
            buyer = Buyer.query.get(head.buyer_id)
            form.buyer_id.data = str(buyer.id) + " - " + buyer.buyer_name

        if head.slaughterhouse_id and head.slaughterhouse_id not in [None, "None", ""]:
            slaughter = Slaughterhouse.query.get(head.slaughterhouse_id)
            form.slaughterhouse_id.data = str(slaughter.id) + " - " + slaughter.slaughterhouse

        form.note_certificate.data = head.note_certificate
        form.note.data = head.note

        return render_template("head/head_update.html", form=form, id=head.id)
