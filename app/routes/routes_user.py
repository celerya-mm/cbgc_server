import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from ..app import db
from ..forms.form_account import FormAccountUpdate, FormUserSignup
from ..models.accounts import User
from ..models.buyers import Buyer
from ..utilitys.functions import event_create, token_admin_validate
from ..utilitys.functions_accounts import psw_contain_usr, psw_verify, psw_hash


@token_admin_validate
@app.route("/user/view/", methods=["GET", "POST"])
def user_view():
    """Visualizzo informazioni User."""
    # Estraggo la lista degli utenti amministratori
    _list = User.query.all()
    _list = [r.to_dict() for r in _list]
    return render_template("user/user_view.html", form=_list)


@token_admin_validate
@app.route("/user/create/", methods=["GET", "POST"])
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
            return render_template("user/user_create.html", form=form)

        contain_usr = psw_contain_usr(form_data["new_password_1"], form_data["username"])
        if contain_usr is not False:
            message = json.loads(json.dumps(contain_usr))
            flash(f"PASSWORD_CONTIENE_UTENTE:")
            flash(message)
            return render_template("user/user_create.html", form=form)

        new_user = User(
            username=form_data["username"].replace(" ", ""),
            name=form_data["name"].strip(),
            last_name=form_data["last_name"].strip(),
            email=form_data["email"].strip(),
            phone=form_data["phone"].strip(),
            password=psw_hash(form_data["new_password_1"].replace(" ", "")),
            note=form_data["note"].strip()
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("UTENTE servizio creato correttamente.")
            return redirect(url_for('user/view'))
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("user/user_create.html", form=form)
    else:
        return render_template("user/user_create.html", form=form)


@token_admin_validate
@app.route("/user/view/history/<_id>", methods=["GET", "POST"])
def user_view_history(_id):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Estraggo l' ID dell'utente corrente
    session["id_user"] = _id

    # Interrogo il DB
    user = User.query.get(_id)
    _user = user.to_dict()

    # Estraggo la storia delle modifiche per l'utente
    history_list = user.events
    history_list = [history.to_dict() for history in history_list]
    len_history = len(history_list)
    return render_template("user/user_view_history.html", form=_user, history_list=history_list, h_len=len_history)


@token_admin_validate
@app.route("/user/update/<_id>", methods=["GET", "POST"])
def user_update(_id):
    """Aggiorna dati Utente."""
    form = FormAccountUpdate()
    if form.validate_on_submit():
        new_data = json.loads(json.dumps(request.form))
        new_data = new_data.to_db()
        # print("USER_FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        user = User.query.get(_id)
        previous_data = user.to_dict()
        # print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        if new_data["buyer_id"] not in ["", "-", None]:
            buyer = Buyer.query.filter_by(buyer_name=new_data["buyer_id"].split(" - ")[0]).first()
            buyer_id = buyer.id
        else:
            buyer_id = None

        new_data["buyer_id"] = buyer_id
        new_data["created_at"] = user.created_at
        new_data["updated_at"] = datetime.now()
        # print("DATA:", json.dumps(administrator.to_dict(), indent=2))
        try:
            db.session.query(User).filter_by(id=_id).update(new_data)
            db.session.commit()
            flash("UTENTE aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("user/user_update.html", form=form, id=_id)

        _event = {
            "username": session["username"],
            "Modification": f"Update account USER whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, user_id=_id):
            return redirect(url_for('user/view/history', _id=_id))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('user/view/history', _id=_id))
    else:
        # recupero i dati
        user = User.query.get(_id)
        # print("USER:", user)
        # print("USER_FIND:", json.dumps(user.to_dict(), indent=2))

        form.username.data = user.username
        form.name.data = user.name
        form.last_name.data = user.last_name
        form.email.data = user.email
        form.phone.data = user.phone
        form.note.data = user.note

        _info = {
            'created_at': user.created_at,
            'updated_at': user.updated_at,
        }
        # print("USER_UPDATE:", json.dumps(form.to_dict(form), indent=2))
        return render_template("user/user_update.html", form=form, id=_id, info=_info)
