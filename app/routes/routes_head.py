import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db
from ..forms.form_head import FormHeadCreate, FormHeadUpdate
from ..models.buyers import Buyer
from ..models.farmers import Farmer
from ..models.heads import Head
from ..models.slaughterhouses import Slaughterhouse
from ..utilitys.functions import event_create, not_empty, token_admin_validate, str_to_date


@token_admin_validate
@app.route("/head/view/", methods=["GET", "POST"])
def head_view():
    """Visualizzo informazioni Capi."""
    _list = Head.query.all()
    _list = [r.to_dict() for r in _list]
    return render_template("head/head_view.html", form=_list)


@token_admin_validate
@app.route("/head/create/", methods=["GET", "POST"])
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
            note=form_data["note"].strip()
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
@app.route("/head/view/history/<_id>", methods=["GET", "POST"])
def head_view_history(_id):
    """Visualizzo la storia delle modifiche al record del Capo."""
    head = Head.query.get(int(_id))
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
    history_list = head.events
    history_list = [history.to_dict() for history in history_list]
    len_history = len(history_list)

    # estraggo il certificato DNA
    dna_list = head.dna_cert
    dna_list = [dna.to_dict() for dna in dna_list]
    len_dna = len(dna_list)

    # estraggo i certificati del consorzio
    cons_list = head.cons_cert
    cons_list = [cert.to_dict() for cert in cons_list]
    len_cons = len(cons_list)
    return render_template(
        "head/head_view_history.html", form=_head,
        history_list=history_list, h_len=len_history,
        dna_list=dna_list, len_dna=len_dna,
        cons_list=cons_list, len_cons=len_cons
    )


@token_admin_validate
@app.route("/head/update/<_id>", methods=["GET", "POST"])
def head_update(_id):
    """Aggiorna dati Capo."""
    form = FormHeadUpdate()
    if form.validate_on_submit():
        new_data = json.loads(json.dumps(request.form))
        new_data = new_data.to_db()
        # print("HEAD_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        head = Head.query.get(_id)
        previous_data = head.to_dict()
        # print("HEAD_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        if new_data["farmer_id"] not in ["", "-", None]:
            farmer = Farmer.query.filter_by(farmer_name=new_data["farmer_id"].split(" - ")[0]).first()
            farmer_id = farmer.id
        else:
            farmer_id = None

        if new_data["buyer_id"] not in ["", "-", None]:
            buyer = Buyer.query.filter_by(buyer_name=new_data["buyer_id"].split(" - ")[0]).first()
            buyer_id = buyer.id
        else:
            buyer_id = None

        if new_data["slaughterhouse_id"] not in ["", "-", None]:
            slaughter = Slaughterhouse.query.filter_by(
                slaughterhouse=new_data["slaughterhouse_id"].split(" - ")[0]).first()
            slaughterhouse_id = slaughter.id
        else:
            slaughterhouse_id = None

        new_data["created_at"] = head.created_at
        new_data["updated_at"] = datetime.now()
        new_data["farmer_id"] = farmer_id
        new_data["buyer_id"] = buyer_id
        new_data["slaughterhouse_id"] = slaughterhouse_id
        # print("HEAD_NEW_DATA:", json.dumps(new_data.to_dict(), indent=2))
        try:
            db.session.query(Head).filter_by(id=_id).update(new_data)
            db.session.commit()
            flash("CAPO aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("user/user_update.html", form=form, id=_id)

        _event = {
            "username": session["username"],
            "Modification": f"Update Head whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, head_id=_id):
            return redirect(url_for('head/view/history', _id=_id))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('head/view/history', _id=_id))
    else:
        # recupero i dati del record
        head = Head.query.get(int(_id))
        # print("HEAD_FIND:", head, type(data))

        form.headset.data = head.headset

        form.birth_date.data = str_to_date(head.birth_date)
        form.castration_date.data = str_to_date(head.castration_date)
        form.slaughter_date.data = str_to_date(head.slaughter_date)
        form.sale_date.data = str_to_date(head.sale_date)

        farmer = Farmer.query.get(head.farmer_id)
        form.farmer_id.data = f"{farmer.id} - {farmer.farmer_name}"

        if head.buyer_id and head.buyer_id not in [None, "None", ""]:
            buyer = Buyer.query.get(head.buyer_id)
            form.buyer_id.data = f"{buyer.id} - {buyer.buyer_name}"

        if head.slaughterhouse_id and head.slaughterhouse_id not in [None, "None", ""]:
            slaughter = Slaughterhouse.query.get(head.slaughterhouse_id)
            form.slaughterhouse_id.data = f"{slaughter.id} - {slaughter.slaughterhouse}"

        form.note_certificate.data = head.note_certificate
        form.note.data = head.note

        _info = {
            'created_at': head.created_at,
            'updated_at': head.updated_at,
        }
        print("HEAD_:", form)
        print("HEAD_FORM:", json.dumps(form.to_dict(), indent=2))
        return render_template("head/head_update.html", form=form, id=_id, info=_info, f_id=head.farmer_id)
