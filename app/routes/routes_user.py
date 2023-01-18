import json

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from app.app import db
from app.forms.form_account import FormAccountUpdate, FormUserSignup
from app.models.accounts import User
from app.utilitys.functions import event_create, token_admin_validate, url_to_json
from app.utilitys.functions_accounts import is_valid_email, psw_contain_usr, psw_verify, psw_hash


@token_admin_validate
@app.route("/user_view/", methods=["GET", "POST"])
def user_view():
    """Visualizzo informazioni User."""
    # Estraggo la lista degli utenti amministratori
    _list = User.query.all()
    _list = [r.to_dict() for r in _list]
    return render_template("user/user_view.html", form=_list)


@token_admin_validate
@app.route("/user_create/", methods=["GET", "POST"])
def user_create():
    """Creazione Utente Consorzio."""
    form = FormUserSignup()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        # print("USER_FORM_DATA", json.dumps(form_data, indent=2))

        verify_password = psw_verify(form_data["new_password_1"])
        if verify_password is not False:
            message = json.loads(json.dumps(verify_password))
            flash(f"PASSWORD_DEBOLE:")
            flash(message)
            return render_template("admin/admin_create.html", form=form)

        contain_usr = psw_contain_usr(form_data["new_password_1"], form_data["username"])
        if contain_usr is not False:
            message = json.loads(json.dumps(contain_usr))
            flash(f"PASSWORD_CONTIENE_UTENTE:")
            flash(message)
            return render_template("admin/admin_create.html", form=form)

        # print("SESSION_ADMIN:", _admin["id"])
        new_user = User(
            username=form_data["username"].replace(" ", ""),
            name=form_data["name"].strip(),
            last_name=form_data["last_name"].strip(),
            email=form_data["email"].strip(),
            phone=form_data["phone"].strip(),
            password=psw_hash(form_data["new_password_1"].replace(" ", "")),
            note=form_data["note"].strip(),
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("UTENTE servizio creato correttamente.")
            return redirect(url_for('admin_view'))
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("user/user_create.html", form=form)
    else:
        return render_template("user/user_create.html", form=form)


@token_admin_validate
@app.route("/user_view_history/<data>", methods=["GET", "POST"])
def user_view_history(data):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Elaboro i dati ricevuti
    data = url_to_json(data)
    print("USER_DATA_PASS:", json.dumps(data, indent=2))

    # Estraggo l' ID dell'utente corrente
    session["id_user"] = data["id"]

    # Interrogo il DB
    user = User.query.filter_by(username=data["username"]).first()
    _user = user.to_dict()
    session["user"] = _user

    # Estraggo la storia delle modifiche per l'utente
    history_list = user.events
    history_list = [history.to_dict() for history in history_list]
    return render_template("user/user_view_history.html", form=_user, history_list=history_list)


@token_admin_validate
@app.route("/user_update/<data>", methods=["GET", "POST"])
def user_update(data):
    """Aggiorna dati Utente."""
    form = FormAccountUpdate()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        print("USER_FORM_DATA_PASS:", json.dumps(form_data, indent=2))
        _id = session["id_user"]
        # print("USER_ID:", _id)
        valid_email = is_valid_email(form_data["email"])
        if valid_email:
            user = User.query.get(_id)
            previous_data = user.to_dict()
            # print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))
            user.username = form_data["username"].replace(" ", "")
            user.name = form_data["name"].strip()
            user.last_name = form_data["last_name"].strip()
            user.email = form_data["email"].strip()
            user.phone = form_data["phone"].strip()
            if form_data["note"] is None:
                user.note = "Null"
            else:
                user.note = form_data["note"].strip()

            # print("NEW_DATA:", json.dumps(user.to_dict(), indent=2))
            try:
                db.session.commit()
                flash("UTENTE aggiornato correttamente.")
            except IntegrityError as err:
                db.session.rollback()
                flash(f"ERRORE: {str(err.orig)}")
                return render_template("user/user_update.html", form=form)

            _event = {
                "username": session["username"],
                "Modification": f"Update account User whit id: {_id}",
                "Previous_data": previous_data
            }
            # print("EVENT:", json.dumps(_event, indent=2))
            if event_create(_event, user_id=_id):
                return redirect(url_for('user_view_history', data=user.to_dict()))
            else:
                flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
                return redirect(url_for('user_view'))
        else:
            form.username.data = form_data["username"]
            form.name.data = form_data["name"]
            form.last_name.data = form_data["last_name"]
            form.email.data = form_data["email"]
            form.phone.data = form_data["phone"]
            form.note.data = form_data["note"]

            flash("ERRORE: la email inserita non è valida.")
            return render_template("user/user_update.html", form=form)
    else:
        # recupero i dati e li converto in dict
        data = url_to_json(data)
        # print("DATA_PASS:", json.dumps(data, indent=2))
        session["id_user"] = data["id"]

        form.username.data = data["username"]
        form.email.data = data["email"]
        form.name.data = data["name"]
        form.last_name.data = data["last_name"]
        form.email.data = data["email"]
        form.phone.data = data["phone"]
        form.note.data = data["note"]

        # print(form.username.data)
        return render_template("user/user_update.html", form=form)
