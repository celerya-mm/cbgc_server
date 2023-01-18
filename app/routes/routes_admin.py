import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from app.app import db
from app.forms.forms import FormPswChange
from app.forms.form_account import FormAccountUpdate, FormAdminSignup
from app.models.accounts import Administrator
from app.utilitys.functions import event_create, token_admin_validate, url_to_json
from app.utilitys.functions_accounts import is_valid_email, psw_contain_usr, psw_verify, psw_hash


@token_admin_validate
@app.route("/admin_view/", methods=["GET", "POST"])
def admin_view():
    """Visualizzo informazioni Utente Amministratore."""
    if "username" in session.keys():
        # Estraggo l'utente amministratore corrente
        admin = Administrator.query.filter_by(username=session["username"]).first()
        _admin = admin.to_dict()
        session["admin"] = _admin

        # Estraggo la lista degli utenti amministratori
        admin_list = Administrator.query.all()
        _admin_list = [admin.to_dict() for admin in admin_list]

        return render_template("admin/admin_view.html", admin=_admin, admin_list=_admin_list)
    else:
        flash(f"Token autenticazione non presente, devi eseguire la Log-In.")
        return redirect(url_for('logout'))


@token_admin_validate
@app.route("/admin_create/", methods=["GET", "POST"])
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

        # print("SESSION_ADMIN:", _admin["id"])
        valid_email = is_valid_email(form_data["email"])
        if valid_email:
            new_admin = Administrator(
                username=form_data["username"].replace(" ", ""),
                name=form_data["name"].strip(),
                last_name=form_data["last_name"].strip(),
                email=form_data["email"].strip(),
                phone=form_data["phone"].strip(),
                password=psw_hash(form_data["new_password_1"].replace(" ", "")),
                note=form_data["note"].strip()
            )
            try:
                db.session.add(new_admin)
                db.session.commit()
                flash("Utente amministratore creato correttamente.")
                return redirect(url_for('admin_view'))
            except IntegrityError as err:
                db.session.rollback()
                flash(f"ERRORE: {str(err.orig)}")
                return render_template("admin/admin_create.html", form=form)
        else:
            form.username.data = form_data["username"]
            form.email.data = form_data["email"]
            form.name.data = form_data["name"]
            form.last_name.data = form_data["last_name"]
            form.note.data = form_data["note"]

            flash("ERRORE: la email inserita non è valida.")
            return render_template("admin/admin_create.html", form=form)
    else:
        return render_template("admin/admin_create.html", form=form)


@token_admin_validate
@app.route("/admin_view_history/<data>", methods=["GET", "POST"])
def admin_view_history(data):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Elaboro i dati ricevuti
    data = url_to_json(data)
    print("DATA_PASS:", json.dumps(data, indent=2))

    # Estraggo l'ID dell'utente amministratore corrente
    session["id_admin"] = data["id"]

    # Interrogo il DB
    admin = Administrator.query.filter_by(username=data["username"]).first()
    _admin = admin.to_dict()
    session["admin"] = _admin

    # Estraggo la storia delle modifiche per l'utente
    history_list = admin.events
    history_list = [history.to_dict() for history in history_list]
    return render_template("admin/admin_view_history.html", form=_admin, history_list=history_list)


@token_admin_validate
@app.route("/admin_update/<data>", methods=["GET", "POST"])
def admin_update(data):
    """Aggiorna Utente Amministratore."""
    form = FormAccountUpdate()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        # print("FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        _id = session["id_admin"]
        # print("ADMIN_ID:", _admin, "TYPE:", type(_admin))
        valid_email = is_valid_email(form_data["email"])
        if valid_email:
            administrator = Administrator.query.get(_id)
            previous_data = administrator.to_dict()
            # print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

            administrator.username = form_data["username"].replace(" ", "")
            administrator.name = form_data["name"].strip()
            administrator.last_name = form_data["last_name"].strip()
            administrator.email = form_data["email"].strip()
            administrator.phone = form_data["phone"].strip()
            administrator.note = form_data["note"].strip()

            # print("DATA:", json.dumps(administrator.to_dict(), indent=2))
            try:
                db.session.commit()
                flash("UTENTE aggiornato correttamente.")
            except IntegrityError as err:
                db.session.rollback()
                flash(f"ERRORE: {str(err.orig)}")
                return render_template("admin/admin_update.html", form=form)

            _event = {
                "username": session["username"],
                "Modification": f"Update account Administrator whit id: {_id}",
                "Previous_data": previous_data
            }
            if event_create(_event, admin_id=_id):
                return redirect(url_for('admin_view_history', data=administrator.to_dict()))
            else:
                flash("ERRORE creazione evento. Ma il record è stato modificato correttamente.")
                return redirect(url_for('admin_view'))
        else:
            form.username.data = form_data["username"]
            form.name.data = form_data["name"]
            form.last_name.data = form_data["last_name"]
            form.email.data = form_data["email"]
            form.phone.data = form_data["phone"]
            form.note.data = form_data["note"]

            flash("ERRORE: la email inserita non è valida.")
            return render_template("admin/admin_update.html", form=form)
    else:
        form = FormAccountUpdate()
        # recupero i dati e li converto in dict
        data = url_to_json(data)
        print("DATA_PASS:", json.dumps(data, indent=2))

        session["id_admin"] = data["id"]

        form.username.data = data["username"]
        form.email.data = data["email"]
        form.name.data = data["name"]
        form.last_name.data = data["last_name"]
        form.email.data = data["email"]
        form.phone.data = data["phone"]
        form.note.data = data["note"]

        print(form.username.data)
        return render_template("admin/admin_update.html", form=form)


@token_admin_validate
@app.route("/admin_update_password/", methods=["GET", "POST"])
def admin_update_password():
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

        old_password = psw_hash(form_data["old_password"])
        # print("OLD:", old_password)
        new_password = psw_hash(form_data["new_password_1"].replace(" ", ""))
        # print("NEW:", new_password)
        administrator = Administrator.query.get(_admin["id"])
        if new_password == administrator.password:
            flash("The 'New Password' inserted is equal to 'Registered Password'.")
            return render_template("admin/admin_update_password.html", form=form)
        elif old_password != administrator.password:
            flash("The 'Current Passwort' inserted does not match the 'Registered Password'.")
            return render_template("admin/admin_update_password.html", form=form)
        else:
            administrator.password = new_password
            administrator.updated_at = datetime.now()

            db.session.commit()
            flash("PASSWORD aggiornata correttamente!")

            _event = {
                "User": session["username"],
                "Modification": "Change Password"
            }
            if event_create(_event, admin_id=_admin["id"]):
                return redirect(url_for('admin_view'))
            else:
                flash("ERRORE creazione evento DB. Ma la password è stata modificata correttamente.")
                return redirect(url_for('admin/admin_view'))
    else:
        return render_template("admin/admin_update_password.html", form=form)
