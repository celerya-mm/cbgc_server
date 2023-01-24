import json

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db
from ..forms.form_cert_cons import FormCertConsCreate, FormCertConsUpdate
from ..models.certificates_cons import CertificateCons, mount_code, year_cert_calc_update
from ..models.buyers import Buyer
from ..models.farmers import Farmer
from ..models.heads import Head
from ..models.slaughterhouses import Slaughterhouse
from ..utilitys.functions import (event_create, not_empty, token_admin_validate, str_to_date,
                                  status_true_false, status_si_no)

VIEW = "/cert_cons/view/"
VIEW_FOR = "cert_cons_view"
VIEW_HTML = "cert_cons/cert_cons_view.html"

CREATE = "/cert_cons/create/<h_id>/<f_id>/<h_set>/"
CREATE_FOR = "cert_cons_create"
CREATE_HTML = "cert_cons/cert_cons_create.html"

HISTORY = "/cert_cons/view/history/<_id>"
HISTORY_FOR = "cert_cons_view_history"
HISTORY_HTML = "cert_cons/cert_cons_view_history.html"

UPDATE = "/cert_cons/update/<_id>"
UPDATE_FOR = "cert_cons_update"
UPDATE_HTML = "cert_cons/cert_cons_update.html"


@token_admin_validate
@app.route(VIEW, methods=["GET", "POST"])
def cert_cons_view():
    """Visualizzo informazioni Capi."""
    from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY
    from ..routes.routes_farmer import HISTORY_FOR as FARMER_HISTORY
    from ..routes.routes_buyer import HISTORY_FOR as BUYER_HISTORY
    from ..routes.routes_slaughterhouse import HISTORY_FOR as SLAUG_HISTORY

    _list = CertificateCons.query.all()
    _list = [r.to_dict() for r in _list]
    return render_template(VIEW_HTML, form=_list, history=HISTORY_FOR, h_hist=HEAD_HISTORY, f_hist=FARMER_HISTORY,
                           b_hist=BUYER_HISTORY, s_hist=SLAUG_HISTORY)


@token_admin_validate
@app.route(CREATE, methods=["GET", "POST"])
def cert_cons_create(h_id, f_id, h_set):
    """Creazione Certificato Consorzio."""
    from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY
    form = FormCertConsCreate()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        # print("HEAD_FORM_DATA", json.dumps(form_data, indent=2))

        new_cert = CertificateCons(
            certificate_id=form_data["certificate_id"],
            certificate_var=form_data["certificate_var"],
            certificate_date=form_data["certificate_date"],
            emitted=form_data["emitted"],

            cockade_id=form_data["cockade_id"],
            cockade_var=form_data["cockade_var"],

            sale_type=form_data["sale_type"],
            sale_quantity=form_data["sale_quantity"],

            invoice_nr=form_data["invoice_nr"],
            invoice_date=form_data["invoice_date"],
            invoice_status=form_data["invoice_status"],

            head_id=int(form_data["head_id"].split(" - ")[0]),
            farmer_id=int(form_data["farmer_id"].split(" - ")[0]),
            buyer_id=int(form_data["buyer_id"].split(" - ")[0]),
            slaughterhouse_id=int(form_data["slaughterhouse_id"].split(" - ")[0]),

            note_certificate=form_data["note_certificate"],
            note=form_data["note"].strip()
        )
        print("CERT_NEW_DATA", json.dumps(new_cert.to_dict(), indent=2))
        try:
            db.session.add(new_cert)
            db.session.commit()
            db.session.close()
            flash("CERTIFICATO CONSORZIO creato correttamente.")
            return redirect(url_for(HEAD_HISTORY, _id=new_cert.head_id))
        except IntegrityError as err:
            db.session.rollback()
            db.session.close()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template(CREATE_HTML, form=form, view=VIEW_FOR)
    else:
        max_id = db.session.query(db.func.max(CertificateCons.id)).scalar()
        prev_cert = CertificateCons.query.get(max_id)
        prev_cert = prev_cert.certificate_nr

        print("HEAD", h_set, "LAST:", prev_cert)
        h_set = f"{int(h_id)} - {h_set}"
        print("HEAD", h_set)

        form.head_id.data = h_set
        form.farmer_id.data = f_id
        return render_template(CREATE_HTML, form=form, view=VIEW_FOR, h_set=h_set, prev_cert=prev_cert)


@token_admin_validate
@app.route(HISTORY, methods=["GET", "POST"])
def cert_cons_view_history(_id):
    """Visualizzo la storia delle modifiche al record del Certificato."""
    from ..routes.routes_head import HISTORY_FOR as HEAD_HISTORY
    from ..routes.routes_farmer import HISTORY_FOR as FARMER_HISTORY
    from ..routes.routes_buyer import HISTORY_FOR as BUYER_HISTORY
    from ..routes.routes_slaughterhouse import HISTORY_FOR as SLAUG_HISTORY
    from ..routes.routes_event import HISTORY_FOR as EVENT_HISTORY

    cert = CertificateCons.query.get(int(_id))
    _cert = cert.to_dict()
    # print("HEAD_FORM:", json.dumps(_head, indent=2), "TYPE:", type(_head))

    if cert.head_id:
        head = Head.query.get(cert.head_id)
        _cert["head_id"] = f"{head.id} - {head.headset}"

    if cert.farmer_id:
        farmer = Farmer.query.get(cert.farmer_id)
        _cert["farmer_id"] = f"{farmer.id} - {farmer.farmer_name}"

    if cert.buyer_id:
        buyer = Buyer.query.get(cert.buyer_id)
        _cert["buyer_id"] = f"{buyer.id} - {buyer.buyer_name}"

    if cert.slaughterhouse_id:
        slaugh = Slaughterhouse.query.get(cert.slaughterhouse_id)  # noqa
        _cert["slaughterhouse_id"] = f"{slaugh.id} - {slaugh.slaughterhouse}"

    # Estraggo la storia delle modifiche per l'utente
    history_list = cert.events
    history_list = [history.to_dict() for history in history_list]

    _cert["emitted"] = status_si_no(_cert["emitted"])
    db.session.close()

    # print("CERT_DATA:", json.dumps(cert.to_dict(), indent=2))
    return render_template(HISTORY_HTML, form=_cert, history_list=history_list, h_len=len(history_list), view=VIEW_FOR,
                           update=UPDATE_FOR, event_history=EVENT_HISTORY,
                           head_history=HEAD_HISTORY, h_id=cert.head_id,
                           farmer_history=FARMER_HISTORY, f_id=cert.farmer_id,
                           buyer_history=BUYER_HISTORY, b_id=cert.buyer_id,
                           slaug_history=SLAUG_HISTORY, s_id=cert.slaughterhouse_id)


@token_admin_validate
@app.route(UPDATE, methods=["GET", "POST"])
def cert_cons_update(_id):
    """Aggiorna dati Capo."""
    form = FormCertConsUpdate()
    if form.validate_on_submit():
        new_data = json.loads(json.dumps(request.form))
        new_data.pop('csrf_token', None)
        # print("HEAD_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        cert = CertificateCons.query.get(int(_id))
        db.session.close()
        previous_data = cert.to_dict()
        # print("HEAD_PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        new_data["certificate_date"] = str_to_date(new_data["certificate_date"])

        new_data["certificate_nr"] = mount_code(
            new_data["certificate_id"], new_data["certificate_year"], new_data["certificate_var"])

        new_data["cockade_id"] = not_empty(new_data["cockade_id"])
        new_data["cockade_nr"] = mount_code(
            new_data["cockade_id"], new_data["certificate_year"], new_data["cockade_var"])

        new_data["emitted"] = status_true_false(new_data["emitted"])
        new_data["invoice_nr"] = not_empty(new_data["invoice_nr"])
        new_data["invoice_date"] = str_to_date(new_data["invoice_date"])

        new_data["sale_quantity"] = not_empty(new_data["sale_quantity"])
        new_data["sale_rest"] = not_empty(new_data["sale_rest"])

        new_data["note_certificate"] = not_empty(new_data["note_certificate"])

        if new_data["head_id"] not in ["", "-", None]:
            new_data["head_id"] = int(new_data["head_id"].split(" - ")[0])
        else:
            new_data["head_id"] = None

        if new_data["buyer_id"] not in ["", "-", None]:
            new_data["buyer_id"] = int(new_data["buyer_id"].split(" - ")[0])
        else:
            new_data["buyer_id"] = None

        if new_data["farmer_id"] not in ["", "-", None]:
            new_data["farmer_id"] = int(new_data["farmer_id"].split(" - ")[0])
        else:
            new_data["farmer_id"] = None

        if new_data["slaughterhouse_id"] not in ["", "-", None]:
            new_data["slaughterhouse_id"] = int(new_data["slaughterhouse_id"].split(" - ")[0])
        else:
            new_data["slaughterhouse_id"] = None

        new_data["created_at"] = cert.created_at

        print("CERT_NEW_DATA:", new_data)
        try:
            db.session.query(CertificateCons).filter_by(id=_id).update(new_data)
            db.session.commit()
            db.session.close()
            flash("CERTIFICATO CONSORZIO aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            db.session.close()
            flash(f"ERRORE: {str(err.orig)}")
            prev_cert = CertificateCons.query.get(int(_id) - 1)
            _info = {
                'created_at': cert.created_at,
                'updated_at': cert.updated_at,
            }
            return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR,
                                   prev_cert=prev_cert.certificate_nr)
            # h_ih=new_data["farmer_id"], f_id=new_data["farmer_id"], b_id=new_data["buyer_id"],
            # s_id=new_data["slaughterhouse_id"])

        _event = {
            "username": session["username"],
            "table": CertificateCons.__tablename__,
            "Modification": f"Update Certificate whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, cert_cons_id=_id):
            return redirect(url_for(HISTORY_FOR, _id=_id))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for(HISTORY_FOR, _id=_id))
    else:
        # recupero i dati del record
        cert = CertificateCons.query.get(int(_id))
        # recupero il record precedente
        max_id = db.session.query(db.func.max(CertificateCons.id)).scalar()
        prev_cert = CertificateCons.query.get(max_id)
        prev_cert = prev_cert.certificate_nr

        # print("HEAD_FIND:", head, type(data))

        form.certificate_id.data = cert.certificate_id
        form.certificate_var.data = cert.certificate_var
        form.certificate_date.data = str_to_date(cert.certificate_date)
        form.certificate_year.data = year_cert_calc_update(cert.certificate_date)

        form.emitted.data = status_si_no(cert.emitted)

        form.cockade_id.data = cert.cockade_id
        form.cockade_var.data = cert.cockade_var

        form.sale_type.data = cert.sale_type
        form.sale_quantity.data = cert.sale_quantity
        form.sale_rest.data = cert.sale_rest

        form.invoice_nr.data = cert.invoice_nr
        form.invoice_date.data = str_to_date(cert.invoice_date)
        form.invoice_status.data = cert.invoice_status

        head = Head.query.get(cert.head_id)
        form.head_id.data = f"{head.id} - {head.headset}"

        farmer = Farmer.query.get(cert.farmer_id)
        form.farmer_id.data = f"{farmer.id} - {farmer.farmer_name}"

        buyer = Buyer.query.get(cert.buyer_id)
        form.buyer_id.data = f"{buyer.id} - {buyer.buyer_name}"

        if cert.slaughterhouse_id:
            slaugh = Slaughterhouse.query.get(cert.slaughterhouse_id)  # noqa
            form.slaughterhouse_id.data = f"{slaugh.id} - {slaugh.slaughterhouse}"

        form.note_certificate.data = cert.note_certificate
        form.note.data = cert.note

        db.session.close()

        _info = {
            'created_at': cert.created_at,
            'updated_at': cert.updated_at,
        }
        print("CERT_:", form)
        print("CERT_FORM:", form.to_dict())
        return render_template(UPDATE_HTML, form=form, id=_id, info=_info, history=HISTORY_FOR,
                               prev_cert=prev_cert)
        # h_ih=head.id, f_id=cert.farmer_id, b_id=buyer.id, s_id=slaugh.id)
