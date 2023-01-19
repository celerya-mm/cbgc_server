import json

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db

from ..models.heads import Head
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
    return render_template("head/head_view.html", form=_list)


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
        # print("HEAD_NEW_DATA", json.dumps(new_head.to_dict(), indent=2))
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
    # Elaboro i dati ricevuti
    date_fields = {
        1: "birth_date",
        2: "castration_date",
        3: "slaughter_date",
        4: "sale_date"
    }
    data = url_to_json(data, date_fields)
    # print("HEAD_DATA_PASS:", json.dumps(data, indent=2))

    # Estraggo l' ID del capo corrente
    session["head_id"] = data["id"]

    # Interrogo il DB
    head = Head.query.filter_by(headset=data["headset"]).first()
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

    # Estraggo la storia delle modifiche per l'utente
    history_list = head.event
    history_list = [history.to_dict() for history in history_list]
    return render_template("head/head_view_history.html", form=_head, history_list=history_list)


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
        head.slaughter_date = not_empty(form_data["slaughter_date"])
        head.sale_date = not_empty(form_data["sale_date"])

        if form_data["farmer_id"] in ["", "-"]:
            head.farmer_id = None
        else:
            farmer = Farmer.query.filter_by(farmer_name=form_data["farmer_id"]).first()
            head.farmer_id = farmer.id

        if form_data["buyer_id"] in ["", "-"]:
            head.buyer_id = None
        else:
            buyer = Buyer.query.filter_by(buyer_name=form_data["buyer_id"]).first()
            head.buyer_id = buyer.id

        if form_data["slaughterhouse_id"] in ["", "-"]:
            head.slaughterhouse_id = None
        else:
            slaughter = Slaughterhouse.query.filter_by(slaughterhouse=form_data["slaughterhouse_id"]).first()
            head.slaughterhouse_id = slaughter.id

        head.note_certificate = not_empty(form_data["note_certificate"])
        head.note = not_empty(form_data["note"])

        # print("HEAD_NEW_DATA:", json.dumps(head.to_dict(), indent=2))
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
            return redirect(url_for('head_view_history', data=head.to_dict()))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('head_view_history', data=head.to_dict()))
    else:
        # recupero i dati e li converto in dict
        date_fields = {
            1: "birth_date",
            2: "castration_date",
            3: "slaughter_date",
            4: "sale_date"
        }
        data = url_to_json(data, date_fields)
        # print("HEAD_DATA_PASS:", json.dumps(data, indent=2))

        session["head_id"] = data["id"]

        form.headset.data = data["headset"]

        form.birth_date.data = str_to_date(data["birth_date"])
        form.castration_date.data = str_to_date(data["castration_date"])
        form.slaughter_date.data = str_to_date(data["slaughter_date"])
        form.sale_date.data = str_to_date(data["sale_date"])

        if data["farmer_id"]:
            try:
                data["farmer_id"] = int(data["farmer_id"].split(" - ")[0])
            except:  # noqa
                pass
            farmer = Farmer.query.get(data["farmer_id"])
            form.farmer_id.data = farmer.farmer_name

        if data["buyer_id"]:
            try:
                data["buyer_id"] = int(data["buyer_id"].split(" - ")[0])
            except:  # noqa
                pass
            buyer = Buyer.query.get(data["buyer_id"])
            form.buyer_id.data = buyer.buyer_name

        if data["slaughterhouse_id"]:
            try:
                data["slaughterhouse_id"] = int(data["slaughterhouse_id"].split(" - ")[0])
            except:  # noqa
                pass
            slaughter = Slaughterhouse.query.get(data["slaughterhouse_id"])
            form.slaughterhouse_id.data = slaughter.slaughterhouse

        form.note_certificate.data = data["note_certificate"]
        form.note.data = data["note"]
        return render_template("head/head_update.html", form=form, id=data["id"])
