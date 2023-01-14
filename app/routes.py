import json
from datetime import datetime
from urllib import parse

from flask import current_app as app, flash, redirect, render_template, session, url_for, request

from .app import db
from .forms import FormAccountUpdate, FormAccountSignup, FormLogin, FormPswChange
from .models.accounts import Administrator, User
from .utility import functions as fnz
from .utility.functions import event_create
from .utility.functions_accounts import is_valid_email
from .utility.psw_function import psw_contain_usr, psw_verify, psw_hash


@app.route("/", methods=["GET", "POST"])
def login():
    """Effettua la log-in."""
    form = FormLogin()
    if form.validate_on_submit():
        print(f"USER: {form.username.data}; PSW: {form.password.data}")
        token = fnz.admin_log_in(form)
        if token is not False:
            session["token_login"] = token
            session["username"] = form.username.data
            return redirect(url_for('admin_view'))
        else:
            flash("Invalid username or password. Please try again!", category="alert")
            return render_template("login.html", form=form)
    else:
        return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Effettua il log-out ed elimina i dati della sessione."""
    session.clear()
    flash("Log-Out effettuato.")
    return redirect(url_for('login'))


@app.route("/admin_view/", methods=["GET", "POST"])
def admin_view():
    """Visualizzo informazioni Utente Amministratore."""
    if "token_login" in session:
        if fnz.token_admin_validate(session["token_login"]):
            pass
        else:
            return redirect(url_for('login'))
        # Estraggo l'utente amministratore corrente
        admin = Administrator.query.filter_by(username=session["username"]).first()
        _admin = admin.to_dict()
        session["admin"] = _admin
        # Estraggo la lista degli utenti amministratori
        admin_list = Administrator.query.all()
        _admin_list = [admin.to_dict() for admin in admin_list]
        return render_template("admin/admin_view.html", admin=_admin, admin_list=_admin_list)
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('logout'))


@app.route("/admin_create/", methods=["GET", "POST"])
def admin_create():
    """Creazione Utente Amministratore."""
    if "token_login" in session:
        if fnz.token_admin_validate(session["token_login"]):
            pass
        else:
            return redirect(url_for('login'))

        form = FormAccountSignup()
        if form.validate_on_submit():
            form_data = json.loads(json.dumps(request.form))
            print("FORM_DATA", json.dumps(form_data, indent=2))

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
                    username=form_data["username"],
                    name=form_data["name"],
                    last_name=form_data["last_name"],
                    email=form_data["email"],
                    password=psw_hash(form_data["new_password_1"]),
                    updated_at=datetime.now()
                )

                db.session.add(new_admin)
                db.session.commit()
                flash("Utente amministratore creato correttamente.")
                return redirect(url_for('admin_view'))
            else:
                form.username.data = form_data["username"]
                form.email.data = form_data["email"]
                form.name.data = form_data["name"]
                form.last_name.data = form_data["last_name"]

                flash("ERROR: the email is not a valid email.")
                return render_template("admin/admin_create.html", form=form)
        else:
            return render_template("admin/admin_create.html", form=form)
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('logout'))


@app.route("/admin_update/<data>", methods=["GET", "POST"])
def admin_update(data):
    """Aggiorna Utente Amministratore."""
    if "token_login" in session:
        if fnz.token_admin_validate(session["token_login"]):
            pass
        else:
            return redirect(url_for('login'))

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

                administrator.username = form_data["username"]
                administrator.name = form_data["name"]
                administrator.last_name = form_data["last_name"]
                administrator.email = form_data["email"]
                administrator.updated_at = datetime.now()

                # print("DATA:", json.dumps(administrator.to_dict(), indent=2))
                db.session.commit()

                _event = {
                    "username": session["username"],
                    "Modification": f"Update account Administrator whit id: {_id}",
                    "Previous_data": previous_data
                }
                if event_create(_event, admin_id=_id):
                    flash("USER update correctly.")
                    return redirect(url_for('admin_view'))
                else:
                    flash("USER update correctly.")
                    flash("ERROR CREATE EVENT BD. But the record changes were done.")
                    return redirect(url_for('admin_view'))
            else:
                form.username.data = form_data["username"]
                form.email.data = form_data["email"]
                form.name.data = form_data["name"]
                form.last_name.data = form_data["last_name"]

                flash("ERROR: the email is not a valid email.")
                return render_template("admin/admin_update.html", form=form)
        else:
            form = FormAccountUpdate()
            # recupero i dati e li converto in dict
            data = parse.unquote(data).replace("'", '"')
            data = json.loads(data)
            print("DATA_PASS:", json.dumps(data, indent=2))
            session["id_admin"] = data["id"]
            form.username.data = data["username"]
            form.email.data = data["email"]
            form.name.data = data["name"]
            form.last_name.data = data["last_name"]
            print(form.username.data)
            return render_template("admin/admin_update.html", form=form)
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('logout'))


@app.route("/admin_update_password/", methods=["GET", "POST"])
def admin_update_password():
    """Aggiorna password Utente Amministratore."""
    if "token_login" in session:
        if fnz.token_admin_validate(session["token_login"]):
            pass
        else:
            return redirect(url_for('logout'))

        form = FormPswChange()
        if form.validate_on_submit():
            form_data = json.loads(json.dumps(request.form))
            _admin = json.loads(json.dumps(session["admin"]))

            verify_password = psw_verify(form_data["new_password_1"])
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
            new_password = psw_hash(form_data["new_password_1"])
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
                flash("Password update correctly!")
                _event = {
                    "User": session["username"],
                    "Modification": "Change Password"
                }
                if event_create(_event, admin_id=_admin["id"]):
                    return redirect(url_for('admin_view'))
                else:
                    flash("ERROR CREATE EVENT. But your password is changed correctly.")
                    return redirect(url_for('admin/admin_view'))
        else:
            return render_template("admin/admin_update_password.html", form=form)
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('logout'))


@app.route("/admin_view_history/<data>", methods=["GET", "POST"])
def admin_view_history(data):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    if "token_login" in session:
        if fnz.token_admin_validate(session["token_login"]):
            pass
        else:
            return redirect(url_for('login'))
        # Elaboro i dati ricevuti
        data = parse.unquote(data).replace("'", '"')
        data = json.loads(data)
        print("DATA_PASS:", json.dumps(data, indent=2))
        # Estraggo l'ID dell'utente amministratore corrente
        session["id_admin"] = data["id"]
        # Interrogo il DB
        admin = Administrator.query.filter_by(username=data["username"]).first()
        _admin = admin.to_dict()
        session["admin"] = _admin
        # Estraggo la storia delle modifiche per l'utente
        history_list = admin.event
        history_list = [history.to_dict() for history in history_list]
        return render_template("admin/admin_view_history.html", admin=_admin, history_list=history_list)
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('logout'))


@app.route("/user_view/", methods=["GET", "POST"])
def user_view():
    """Visualizzo informazioni User."""
    if "token_login" in session:
        if fnz.token_admin_validate(session["token_login"]):
            pass
        else:
            return redirect(url_for('login'))
        # Estraggo la lista degli utenti amministratori
        user_list = User.query.all()
        _user_list = [user.to_dict() for user in user_list]
        return render_template("user/user_view.html", user_list=_user_list)
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('logout'))


@app.route("/user_create/", methods=["GET", "POST"])
def user_create():
    """Creazione Utente Consorzio."""
    if "token_login" in session:
        if fnz.token_admin_validate(session["token_login"]):
            pass
        else:
            return redirect(url_for('logout'))

        form = FormAccountSignup()
        if form.validate_on_submit():
            form_data = json.loads(json.dumps(request.form))
            print("FORM_DATA", json.dumps(form_data, indent=2))

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
                new_user = User(
                    username=form_data["username"],
                    name=form_data["name"],
                    last_name=form_data["last_name"],
                    email=form_data["email"],
                    password=psw_hash(form_data["new_password_1"]),
                    updated_at=datetime.now()
                )

                db.session.add(new_user)
                db.session.commit()
                flash("Utente creato correttamente.")
                return redirect(url_for('user_view'))
            else:
                form.username.data = form_data["username"]
                form.email.data = form_data["email"]
                form.name.data = form_data["name"]
                form.last_name.data = form_data["last_name"]
                flash("ERROR: the email is not a valid email.")
                return render_template("user/user_create.html", form=form)
        else:
            return render_template("user/user_create.html", form=form)
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('logout'))


@app.route("/user_update/<data>", methods=["GET", "POST"])
def user_update(data):
    """Aggiorna dati Utente."""
    if "token_login" in session:
        if fnz.token_admin_validate(session["token_login"]):
            pass
        else:
            return redirect(url_for('login'))

        form = FormAccountUpdate()
        if form.validate_on_submit():
            form_data = json.loads(json.dumps(request.form))
            print("FORM_DATA_PASS:", json.dumps(form_data, indent=2))
            _id = session["id_user"]
            print("USER_ID:", _id)
            valid_email = is_valid_email(form_data["email"])
            if valid_email:
                user = User.query.get(_id)
                previous_data = user.to_dict()
                print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

                user.username = form_data["username"]
                user.name = form_data["name"]
                user.last_name = form_data["last_name"]
                user.email = form_data["email"]
                user.updated_at = datetime.now()

                print("DATA:", json.dumps(user.to_dict(), indent=2))
                db.session.commit()

                _event = {
                    "username": session["username"],
                    "Modification": f"Update account User whit id: {_id}",
                    "Previous_data": previous_data
                }
                print("EVENT:", json.dumps(_event, indent=2))
                if event_create(_event, user_id=_id):
                    flash("USER update correctly.")
                    return redirect(url_for('user_view'))
                else:
                    flash("USER update correctly.")
                    flash("ERROR CREATE EVENT BD. But the record changes were done.")
                    return redirect(url_for('user_view'))
            else:
                form.username.data = form_data["username"]
                form.email.data = form_data["email"]
                form.name.data = form_data["name"]
                form.last_name.data = form_data["last_name"]

                flash("ERROR: the email is not a valid email.")
                return render_template("user/user_update.html", form=form)
        else:
            form = FormAccountUpdate()
            # recupero i dati e li converto in dict
            data = parse.unquote(data).replace("'", '"')
            data = json.loads(data)
            print("DATA_PASS:", json.dumps(data, indent=2))
            session["id_user"] = data["id"]
            form.username.data = data["username"]
            form.email.data = data["email"]
            form.name.data = data["name"]
            form.last_name.data = data["last_name"]
            print(form.username.data)
            return render_template("user/user_update.html", form=form)
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('logout'))


@app.route("/user_view_history/<data>", methods=["GET", "POST"])
def user_view_history(data):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    if "token_login" in session:
        if fnz.token_admin_validate(session["token_login"]):
            pass
        else:
            return redirect(url_for('login'))
        # Elaboro i dati ricevuti
        data = parse.unquote(data).replace("'", '"')
        data = json.loads(data)
        print("DATA_PASS:", json.dumps(data, indent=2))
        # Estraggo l' ID dell'utente corrente
        session["id_user"] = data["id"]
        # Interrogo il DB
        user = User.query.filter_by(username=data["username"]).first()
        _user = user.to_dict()
        session["user"] = _user
        # Estraggo la storia delle modifiche per l'utente
        history_list = user.event
        history_list = [history.to_dict() for history in history_list]
        return render_template("user/user_view_history.html", user=_user, history_list=history_list)
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('logout'))
