import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, url_for, request, session
from sqlalchemy.exc import IntegrityError

from ..app import db
from ..forms.form_buyer import FormBuyerCreate, FormBuyerUpdate
from ..models.accounts import User
from ..models.buyers import Buyer
from ..models.heads import Head
from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY
from ..utilitys.functions import (event_create, status_si_no, status_true_false, str_to_date, token_admin_validate,
                                  address_mount)

VIEW = "/buyer/view/"
VIEW_FOR = "buyer_view"
VIEW_HTML = "buyer/buyer_view.html"

CREATE = "/buyer/create/"
CREATE_FOR = "buyer_create"
CREATE_HTML = "buyer/buyer_create.html"

HISTORY = "/buyer/view/history/<_id>"
HISTORY_FOR = "buyer_view_history"
HISTORY_HTML = "buyer/buyer_view_history.html"

UPDATE = "/buyer/update/<_id>"
UPDATE_FOR = "buyer_update"
UPDATE_HTML = "buyer/buyer_update.html"


@token_admin_validate
@app.route(VIEW, methods=["GET", "POST"])
def buyer_view():
    """Visualizza informazioni Acquirenti."""
    # Estraggo la lista degli allevatori
    _list = Buyer.query.all()
    _list = [r.to_dict() for r in _list]
    return render_template(VIEW_HTML, form=_list, create=CREATE_FOR, update=UPDATE_FOR, history=HISTORY_FOR)


@token_admin_validate
@app.route(CREATE, methods=["GET", "POST"])
def buyer_create():
    """Creazione Acquirente Consorzio."""
    form = FormBuyerCreate()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        # print("BUYER_FORM_DATA", json.dumps(form_data, indent=2))

        user_id = User.query.filter_by(username=form_data["user_id"]).first()
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
            affiliation_status=status_true_false(form_data["affiliation_status"]),

            user_id=user_id.id,

            note_certificate=form_data["note_certificate"].strip(),
            note=form_data["note"].strip()
        )
        try:
            db.session.add(new_farmer)
            db.session.commit()
            flash("ACQUIRENTE creato correttamente.")
            return redirect(url_for(HISTORY_FOR))
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template(CREATE_HTML, form=form, view=VIEW_FOR)
    else:
        return render_template(CREATE_HTML, form=form, view=VIEW_FOR)


@token_admin_validate
@app.route(HISTORY, methods=["GET", "POST"])
def buyer_view_history(_id):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Interrogo il DB
    buyer = Buyer.query.get(int(_id))
    _buyer = buyer.to_dict()

    # Estraggo l'utente collegato
    if buyer.user_id:
        user = User.query.get(buyer.user_id)
        _buyer["user_full"] = f"{buyer.user_id} - {user.username}"
        # print("BUYER_VIEW_DATA:", json.dumps(_buyer, indent=2), "TYPE:", type(_buyer))

    # Estraggo la storia delle modifiche per l'utente
    history_list = buyer.events
    history_list = [history.to_dict() for history in history_list]
    len_history = len(history_list)

    # estraggo i certificati del consorzio e i capi acquistati
    cons_list = buyer.cons_certs
    _cons_list = [cert.to_dict() for cert in cons_list]

    head_list = []
    for cert in cons_list:
        _h = Head.query.get(cert.head_id)
        if _h and _h not in head_list:
            head_list.append(_h.to_dict())

    return render_template(HISTORY_HTML, form=_buyer, history_list=history_list, h_len=len_history, view=VIEW_FOR,
                           update=UPDATE_FOR, cons_list=_cons_list, len_cons=len(_cons_list),
                           head_list=head_list, len_heads=len(head_list), head_history=HEAD_HISTORY)


@token_admin_validate
@app.route(UPDATE, methods=["GET", "POST"])
def buyer_update(_id):
    """Aggiorna dati Acquirente."""
    form = FormBuyerUpdate()
    if form.validate_on_submit():
        # recupero i dati e li converto in dict
        new_data = json.loads(json.dumps(request.form))
        new_data.pop('csrf_token', None)
        # print("BUYER_UPDATE_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        buyer = Buyer.query.get(_id)
        previous_data = buyer.to_dict()
        # print("BUYER_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        new_data["full_address"] = address_mount(new_data["address"], new_data["cap"], new_data["city"])
        new_data["affiliation_status"] = status_true_false(new_data["affiliation_status"])

        if new_data["user_id"] not in ["", "-", None]:
            new_data["user_id"] = int(new_data["user_id"].split(" - ")[0])
        else:
            new_data["user_id"] = None

        new_data["created_at"] = buyer.created_at
        new_data["updated_at"] = datetime.now()
        print("NEW_DATA:", new_data)
        try:
            db.session.query(Buyer).filter_by(id=_id).update(new_data)
            db.session.commit()
            flash("ACQUIRENTE aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            _info = {
                'created_at': buyer.created_at,
                'updated_at': buyer.updated_at,
            }
            return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)

        _event = {
            "username": session["username"],
            "Modification": f"Update Buyer whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("BUYER_EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, buyer_id=_id):
            return redirect(url_for(HISTORY_FOR, _id=_id))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for(HISTORY_FOR, _id=_id))
    else:
        # recupero i dati del record
        buyer = Buyer.query.get(int(_id))
        # print("BUYER_FIND:", buyer, type(buyer))

        form.buyer_name.data = buyer.buyer_name
        form.buyer_type.data = buyer.buyer_type

        form.email.data = buyer.email
        form.phone.data = buyer.phone

        form.address.data = buyer.address
        form.cap.data = buyer.cap
        form.city.data = buyer.city

        form.affiliation_start_date.data = str_to_date(buyer.affiliation_start_date)
        form.affiliation_end_date.data = str_to_date(buyer.affiliation_end_date)
        form.affiliation_status.data = status_si_no(buyer.affiliation_status)

        form.note_certificate.data = buyer.note_certificate
        form.note.data = buyer.note

        _info = {
            'created_at': buyer.created_at,
            'updated_at': buyer.updated_at,
        }
        # print("BUYER_:", form)
        # print("BUYER_FORM:", json.dumps(form.to_dict(form), indent=2))
        return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)
