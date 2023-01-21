import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db
from ..forms.form_account import FormAccountUpdate, FormAdminSignup
from ..forms.forms import FormPswChange
from ..models.accounts import Administrator
from ..utilitys.functions import event_create, token_admin_validate
from ..utilitys.functions_accounts import psw_contain_usr, psw_verify, psw_hash


@token_admin_validate
@app.route("/admin/view/", methods=["GET", "POST"])
def admin_view():
    """Visualizzo informazioni Utente Amministratore."""
    if "username" in session.keys():
        # Estraggo l'utente amministratore corrente
        admin = Administrator.query.filter_by(username=session["username"]).first()
        _admin = admin.to_dict()
        session["admin"] = _admin

        # Estraggo la lista degli utenti amministratori
        _list = Administrator.query.all()
        _list = [r.to_dict() for r in _list]
        return render_template("admin/admin_view.html", admin=_admin, form=_list)
    else:
        flash(f"Token autenticazione non presente, devi eseguire la Log-In.")
        return redirect(url_for('logout'))


@token_admin_validate
@app.route("/admin/create/", methods=["GET", "POST"])
def admin_create():
    """Creazione Utente Amministratore."""
    form = FormAdminSignup()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        # print("FORM_DATA", json.dumps(form_data, indent=2))

        verify_password = psw_verify(form_data["new_password_1"])
        if verify_password is not False:
            message = json.loads(json.dumps(verify_password))
            flash(f"PASSWORD_WEAK:")
            flash(message)
            return render_template("admin/admin_create.html", form=form)

        contain_usr = psw_contain_usr(form_data["new_password_1"], form_data["username"])
        if contain_usr is not False:
            message = json.loads(json.dumps(contain_usr))
            flash(f"PASSWORD_CONTAIN_USER:")
            flash(message)
            return render_template("admin/admin_create.html", form=form)

        new_admin = Administrator(
            username=form_data["username"].replace(" ", ""),
            name=form_data["name"].strip(),
            last_name=form_data["last_name"].strip(),
            email=form_data["email"].strip(),
            phone=form_data["phone"].strip(),
            password=psw_hash(form_data["new_password_1"].replace(" ", "")),
            note=form_data["note"].strip(),
        )
        try:
            db.session.add(new_admin)
            db.session.commit()
            flash("Utente amministratore creato correttamente.")
            return redirect(url_for('admin/view'))
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("admin/admin_create.html", form=form)
    else:
        return render_template("admin/admin_create.html", form=form)


@token_admin_validate
@app.route("/admin/view/history/<_id>", methods=["GET", "POST"])
def admin_view_history(_id):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Estraggo l'ID dell'utente amministratore corrente
    session["id_admin"] = _id

    # Interrogo il DB
    admin = Administrator.query.get(_id)
    _admin = admin.to_dict()

    # Estraggo la storia delle modifiche per l'utente
    history_list = admin.events
    history_list = [history.to_dict() for history in history_list]
    len_history = len(history_list)

    return render_template("admin/admin_view_history.html", form=_admin, history_list=history_list, h_len=len_history)


@token_admin_validate
@app.route("/admin/update/<_id>", methods=["GET", "POST"])
def admin_update(_id):
    """Aggiorna Utente Amministratore."""
    form = FormAccountUpdate()
    if form.validate_on_submit():
        new_data = json.loads(json.dumps(request.form))
        new_data = new_data.to_db()
        # print("FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        administrator = Administrator.query.get(_id)
        previous_data = administrator.to_dict()
        # print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        new_data["created_at"] = administrator.created_at
        new_data["updated_at"] = datetime.now()
        # print("DATA:", json.dumps(administrator.to_dict(), indent=2))
        try:
            db.session.query(Administrator).filter_by(id=_id).update(new_data)
            db.session.commit()
            flash("UTENTE aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("admin/admin_update.html", form=form, id=_id)

        _event = {
            "username": session["username"],
            "Modification": f"Update account Administrator whit id: {_id}",
            "Previous_data": previous_data
        }
        if event_create(_event, admin_id=_id):
            return redirect(url_for('admin/view/history', _id=_id))
        else:
            flash("ERRORE creazione evento. Ma il record è stato modificato correttamente.")
            return redirect(url_for('admin/view/history', _id=_id))

    else:
        # recupero i dati
        admin = Administrator.query.get(_id)
        # print("ADMIN:", admin)
        # print("ADMIN_FIND:", json.dumps(admin.to_dict(), indent=2))

        form.username.data = admin.username
        form.name.data = admin.name
        form.last_name.data = admin.last_name
        form.email.data = admin.email
        form.phone.data = admin.phone
        form.note.data = admin.note

        _info = {
            'created_at': admin.created_at,
            'updated_at': admin.updated_at,
        }
        # print("ADMIN_UPDATE:", json.dumps(form.to_dict(form), indent=2))
        return render_template("admin/admin_update.html", form=form, id=_id, info=_info)


@token_admin_validate
@app.route("/admin/update/password/<_id>", methods=["GET", "POST"])
def admin_update_password(_id):
    """Aggiorna password Utente Amministratore."""
    form = FormPswChange()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        _admin = json.loads(json.dumps(session["admin"]))

        verify_password = psw_verify(form_data["new_password_1"].replace(" ", ""))
        if verify_password is not False:
            message = json.loads(json.dumps(verify_password))
            flash(f"PASSWORD_WEAK:")
            flash(message)
            return render_template("admin/admin_update_password.html", form=form)

        contain_usr = psw_contain_usr(form_data["new_password_1"], _admin["username"])
        if contain_usr is not False:
            message = json.loads(json.dumps(contain_usr))
            flash(f"PASSWORD_CONTAIN_USER:")
            flash(message)
            return render_template("admin/admin_update_password.html", form=form)

        old_password = psw_hash(form_data["old_password"].replace(" ", "").strip())
        # print("OLD:", old_password)
        new_password = psw_hash(form_data["new_password_1"].replace(" ", "").strip())
        # print("NEW:", new_password)

        administrator = Administrator.query.get(_id)

        if new_password == administrator.password:
            flash("The 'New Password' inserted is equal to 'Registered Password'.")
            return render_template("admin/admin_update_password.html", form=form, id=_id)
        elif old_password != administrator.password:
            flash("The 'Current Passwort' inserted does not match the 'Registered Password'.")
            return render_template("admin/admin_update_password.html", form=form, id=_id)
        else:
            administrator.password = new_password
            administrator.updated_at = datetime.now()

            db.session.commit()
            flash("PASSWORD aggiornata correttamente! Effettua una nuova Log-In.")
            _event = {
                "username": session["username"],
                "Modification": "Password changed"
            }
            if event_create(_event, admin_id=_id):
                return redirect(url_for('logout'))
            else:
                flash("ERRORE creazione evento DB. Ma la password è stata modificata correttamente.")
                return redirect(url_for('logout'))
    else:
        return render_template("admin/admin_update_password.html", form=form, id=_id)
