import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db
from ..forms.form_head import FormHeadCreate, FormHeadUpdate
from ..models.buyers import Buyer
from ..models.farmers import Farmer
from ..models.heads import Head, verify_castration
from ..models.slaughterhouses import Slaughterhouse
from ..routes.routes_cert_dna import HISTORY_FOR as DNA_HISTORY
from ..utilitys.functions import event_create, not_empty, token_admin_validate, str_to_date, year_extract

VIEW = "/head/view/"
VIEW_FOR = "head_view"
VIEW_HTML = "head/head_view.html"

CREATE = "/head/create/"
CREATE_FOR = "head_create"
CREATE_HTML = "head/head_create.html"

HISTORY = "/head/view/history/<_id>"
HISTORY_FOR = "head_view_history"
HISTORY_HTML = "head/head_view_history.html"

UPDATE = "/head/update/<_id>"
UPDATE_FOR = "head_update"
UPDATE_HTML = "head/head_update.html"


@token_admin_validate
@app.route(VIEW, methods=["GET", "POST"])
def head_view():
    """Visualizzo informazioni Capi."""
    _list = Head.query.all()
    _list = [r.to_dict() for r in _list]
    return render_template(VIEW_HTML, form=_list, create=CREATE_FOR, update=UPDATE_FOR, history=HISTORY_FOR)


@token_admin_validate
@app.route(CREATE, methods=["GET", "POST"])
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
            return render_template(CREATE_HTML, form=form, view=VIEW_FOR)
    else:
        return render_template(CREATE_HTML, form=form, view=VIEW_FOR)


@token_admin_validate
@app.route(HISTORY, methods=["GET", "POST"])
def head_view_history(_id):
    """Visualizzo la storia delle modifiche al record del Capo."""
    from ..routes.routes_cert_dna import CREATE_FOR as DNA_CREATE_FOR
    head = Head.query.get(int(_id))
    _head = head.to_dict()
    # print("HEAD_FORM:", json.dumps(_head, indent=2), "TYPE:", type(_head))

    if head.farmer_id:
        farmer = Farmer.query.get(head.farmer_id)
        _head["farmer_id"] = f"{farmer.id} - {farmer.farmer_name}"

    # Estraggo la storia delle modifiche per l'utente
    history_list = head.events
    history_list = [history.to_dict() for history in history_list]

    # estraggo il certificato DNA
    dna_list = head.dna_cert
    dna_list = [dna.to_dict() for dna in dna_list]

    # estraggo i certificati del consorzio, i compratori e i macelli
    cons_list = head.cons_cert
    _cons_list = [cert.to_dict() for cert in cons_list]

    buyer_list = []
    for cert in cons_list:
        _b = Buyer.query.get(cert.buyer_id)
        if _b and _b not in buyer_list:
            buyer_list.append(_b.to_dict())

    slaug_list = []
    for cert in cons_list:
        _s = Slaughterhouse.query.get(cert.slaughterhouse_id)
        if _s and _s not in slaug_list:
            slaug_list.append(_s.to_dict())

    print("LISTA_BUYERS:", json.dumps(buyer_list, indent=2))
    print("LISTA_SLAUGHTERHOUSES:", json.dumps(slaug_list, indent=2))

    return render_template(HISTORY_HTML, form=_head, history_list=history_list, h_len=len(history_list), view=VIEW_FOR,
                           update=UPDATE_FOR,
                           dna_list=dna_list, len_dna=len(dna_list), dna_create=DNA_CREATE_FOR, dna_history=DNA_HISTORY,
                           cons_list=_cons_list, len_cons=len(_cons_list),
                           buyer_list=buyer_list, len_buyers=len(buyer_list),
                           slaug_list=slaug_list, len_slaug=len(slaug_list))


@token_admin_validate
@app.route(UPDATE, methods=["GET", "POST"])
def head_update(_id):
    """Aggiorna dati Capo."""
    from ..routes.routes_cert_dna import CREATE_FOR as DNA_CREATE_FOR

    form = FormHeadUpdate()
    if form.validate_on_submit():
        new_data = json.loads(json.dumps(request.form))
        new_data.pop('csrf_token', None)
        # print("HEAD_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        head = Head.query.get(_id)
        previous_data = head.to_dict()
        # print("HEAD_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        new_data["birth_year"] = year_extract(new_data["birth_date"])
        new_data["castration_year"] = year_extract(new_data["castration_date"])
        new_data["castration_compliance"] = verify_castration(new_data["birth_date"], new_data["castration_date"])
        new_data["sale_year"] = year_extract(new_data["sale_date"])

        if new_data["farmer_id"] not in ["", "-", None]:
            new_data["farmer_id"] = int(new_data["farmer_id"].split(" - ")[0])
        else:
            new_data["farmer_id"] = None

        new_data["created_at"] = head.created_at
        new_data["updated_at"] = datetime.now()

        print("NEW_DATA:", new_data)
        try:
            db.session.query(Head).filter_by(id=_id).update(new_data)
            db.session.commit()
            flash("CAPO aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            _info = {
                'created_at': head.created_at,
                'updated_at': head.updated_at,
            }
            return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR)

        _event = {
            "username": session["username"],
            "Modification": f"Update Head whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, head_id=_id):
            return redirect(url_for(HISTORY_FOR, _id=_id))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for(HISTORY_FOR, _id=_id))
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

        form.note_certificate.data = head.note_certificate
        form.note.data = head.note

        _info = {
            'created_at': head.created_at,
            'updated_at': head.updated_at,
        }
        print("HEAD_:", form)
        print("HEAD_FORM:", json.dumps(form.to_dict(), indent=2))
        return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR, f_id=head.farmer_id,
                               dna_create=DNA_CREATE_FOR)
