import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db
from ..forms.form_cert_dna import FormCertDnaCreate, FormCertDnaUpdate
from ..models.certificates_dna import CertificateDna
from ..models.heads import Head
from ..models.farmers import Farmer
from ..utilitys.functions import event_create, token_admin_validate


@token_admin_validate
@app.route("/cert_dna/view/", methods=["GET", "POST"])
def cert_dna_view():
    """Visualizzo informazioni Certificato."""
    # Estraggo la lista degli utenti amministratori
    _list = CertificateDna.query.all()
    _list = [r.to_dict() for r in _list]
    return render_template("cert_dna/cert_dna_view.html", form=_list)


@token_admin_validate
@app.route("/cert_dna/create/<h_id>/<f_id>/<h_set>/", methods=["GET", "POST"])
def cert_dna_create(h_id, f_id, h_set):
    """Creazione Certificato DNA."""
    form = FormCertDnaCreate()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        print("DNA_FORM_DATA", json.dumps(form_data, indent=2))
        
        new_data = CertificateDna(
            dna_cert_id=form_data["dna_cert_id"].strip(),
            dna_cert_date=form_data["dna_cert_date"],
            head_id=int(h_id),
            farmer_id=int(f_id.split(" - ")[0]),
            note=form_data["note"].strip()
        )
        print("NEW_DATA:", json.dumps(new_data.to_dict(), indent=2))
        try:
            db.session.add(new_data)
            db.session.commit()
            flash("CERTIFICATO DNA creato correttamente.")
            return redirect(url_for('head_view_history', _id=new_data.head_id))
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("cert_dna/cert_dna_create.html", form=form)
    else:
        h_set = f"{int(h_id)} - {h_set}"
        return render_template("cert_dna/cert_dna_create.html", form=form, f_id=f_id, h_set=h_set, h_id=h_id)


@token_admin_validate
@app.route("/cert_dna/view_history/<_id>", methods=["GET", "POST"])
def cert_dna_view_history(_id):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Estraggo l' ID dell'utente corrente
    session["id_user"] = _id

    # Interrogo il DB
    cert_dna = CertificateDna.query.get(_id)
    _cert_dna = cert_dna.to_dict()

    # estraggo capo
    _head = Head.query.get(cert_dna.head_id)
    _head = _head.to_dict()

    # estraggo allevatore
    _farmer = Farmer.query.get(cert_dna.farmer_id)
    _farmer = _farmer.to_dict()

    # Estraggo la storia delle modifiche
    history_list = cert_dna.events
    history_list = [history.to_dict() for history in history_list]
    len_history = len(history_list)
    return render_template("cert_dna/cert_dna_view_history.html", form=_cert_dna, history_list=history_list,
                           head=_head, farmer=_farmer, h_len=len_history)


@token_admin_validate
@app.route("/cert_dna/update/<_id>", methods=["GET", "POST"])
def cert_dna_update(_id):
    """Aggiorna dati Utente."""
    form = FormCertDnaUpdate()
    if form.validate_on_submit():
        new_data = json.loads(json.dumps(request.form))
        new_data = new_data.to_db()
        # print("USER_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        _cert = CertificateDna.query.get(_id)
        previous_data = _cert.to_dict()
        # print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        new_data["created_at"] = _cert.created_at
        new_data["updated_at"] = datetime.now()
        # print("DATA:", json.dumps(administrator.to_dict(), indent=2))
        try:
            db.session.query(CertificateDna).filter_by(id=_id).update(new_data)
            db.session.commit()
            flash("CERTIFICATO aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("cert_dna/cert_dna_update.html", form=form, id=_id, h_id=_cert.id)

        _event = {
            "username": session["username"],
            "Modification": f"Update Certificate DNA whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, cert_dna_id=_id):
            return redirect(url_for('head_view_history', _id=new_data["head_id"]))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('head_view_history', _id=new_data["head_id"]))
    else:
        # recupero i dati
        _cert = CertificateDna.query.get(_id)
        # print("USER:", user)
        # print("USER_FIND:", json.dumps(user.to_dict(), indent=2))

        # recupera Capo
        _head = Head.query.get(_cert.head_id)

        # recupera Allevatore
        _farmer = Head.query.get(_cert.farmer_id)

        form.dna_cert_id.data = _cert.dna_cert_id
        form.dna_cert_date.data = _cert.dna_cert_date
        form.head_id.data = f"{_head.id} - {_head.headset}"
        form.farmer_id.data = f"{_farmer.id} - {_farmer.farmer_name}"
        form.note.data = _cert.note

        _info = {
            'created_at': _cert.created_at,
            'updated_at': _cert.updated_at,
        }
        # print("USER_UPDATE:", json.dumps(form.to_dict(form), indent=2))
        return render_template("cert_dna/cert_dna_update.html", form=form, id=_id, info=_info, h_id=_head.id)
