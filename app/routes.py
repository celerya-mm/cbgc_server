import json
from datetime import datetime

from flask import current_app as app, flash, redirect, render_template, session, url_for, request
from sqlalchemy.exc import IntegrityError

from .app import db
from .forms import (FormAccountUpdate, FormAccountSignup, FormLogin, FormPswChange, FormFarmer, FormBuyer)
from .models.accounts import Administrator, User
from .models.buyers import Buyer
from .models.farmers import Farmer
from .utility.functions import admin_log_in, event_create, token_admin_validate, url_to_json
from .utility.functions_accounts import is_valid_email, psw_contain_usr, psw_verify, psw_hash


@app.route("/", methods=["GET", "POST"])
def login():
    """Effettua la log-in."""
    form = FormLogin()
    if form.validate_on_submit():
        print(f"USER: {form.username.data}; PSW: {form.password.data}")
        token = admin_log_in(form)
        if token:
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
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

    # Estraggo l'utente amministratore corrente
    admin = Administrator.query.filter_by(username=session["username"]).first()
    _admin = admin.to_dict()
    session["admin"] = _admin

    # Estraggo la lista degli utenti amministratori
    admin_list = Administrator.query.all()
    _admin_list = [admin.to_dict() for admin in admin_list]

    return render_template("admin/admin_view.html", admin=_admin, admin_list=_admin_list)


@app.route("/admin_create/", methods=["GET", "POST"])
def admin_create():
    """Creazione Utente Amministratore."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

    form = FormAccountSignup()
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


@app.route("/admin_update/<data>", methods=["GET", "POST"])
def admin_update(data):
    """Aggiorna Utente Amministratore."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

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


@app.route("/admin_update_password/", methods=["GET", "POST"])
def admin_update_password():
    """Aggiorna password Utente Amministratore."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

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


@app.route("/admin_view_history/<data>", methods=["GET", "POST"])
def admin_view_history(data):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

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


@app.route("/user_view/", methods=["GET", "POST"])
def user_view():
    """Visualizzo informazioni User."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

    # Estraggo la lista degli utenti amministratori
    user_list = User.query.all()
    _user_list = [user.to_dict() for user in user_list]
    return render_template("user/user_view.html", user_list=_user_list)


@app.route("/user_create/", methods=["GET", "POST"])
def user_create():
    """Creazione Utente Consorzio."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

    form = FormAccountSignup()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        # print("FORM_DATA", json.dumps(form_data, indent=2))

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
        valid_email = is_valid_email(form_data["email"])
        if valid_email:
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
            form.username.data = form_data["username"]
            form.email.data = form_data["email"]
            form.name.data = form_data["name"]
            form.last_name.data = form_data["last_name"]
            form.note.data = form_data["note"]

            flash("ERRORE: la email inserita non è valida.")
            return render_template("user/user_create.html", form=form)
    else:
        return render_template("user/user_create.html", form=form)


@app.route("/user_update/<data>", methods=["GET", "POST"])
def user_update(data):
    """Aggiorna dati Utente."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

    form = FormAccountUpdate()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        print("FORM_DATA_PASS:", json.dumps(form_data, indent=2))
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


@app.route("/user_view_history/<data>", methods=["GET", "POST"])
def user_view_history(data):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

    # Elaboro i dati ricevuti
    data = url_to_json(data)
    print("DATA_PASS:", json.dumps(data, indent=2))

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


@app.route("/farmer_view/", methods=["GET", "POST"])
def farmer_view():
    """Visualizzo informazioni Allevatori."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

    # Estraggo la lista degli allevatori
    farmer_list = Farmer.query.all()
    _farmer_list = [farmer.to_dict() for farmer in farmer_list]
    return render_template("farmer/farmer_view.html", farmer_list=_farmer_list)


@app.route("/farmer_create/", methods=["GET", "POST"])
def farmer_create():
    """Creazione Allevatore Consorzio."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

    form = FormFarmer()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        print("FORM_DATA", json.dumps(form_data, indent=2))
        if form_data["affiliation_status"] == "NO":
            form_data["affiliation_status"] = False
        else:
            form_data["affiliation_status"] = True

        new_farmer = Farmer(
            farmer_name=form_data["farmer_name"].strip(),

            email=form_data["email"].strip(),
            phone=form_data["phone"].strip(),

            address=form_data["address"].strip(),
            cap=form_data["cap"].strip(),
            city=form_data["city"].strip(),

            affiliation_start_date=form_data["affiliation_start_date"],
            affiliation_status=form_data["affiliation_status"],

            stable_code=form_data["stable_code"],
            stable_type=form_data["stable_type"],
            stable_productive_orientation=form_data["stable_productive_orientation"],
            stable_breeding_methods=form_data["stable_breeding_methods"],

            note_certificate=form_data["note_certificate"],
            note=form_data["note"]
        )
        try:
            db.session.add(new_farmer)
            db.session.commit()
            flash("ALLEVATORE creato correttamente.")
            return redirect(url_for('farmer_view'))
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("farmer/farmer_create.html", form=form)
    else:
        return render_template("farmer/farmer_create.html", form=form)


@app.route("/farmer_update/<data>", methods=["GET", "POST"])
def farmer_update(data):
    """Aggiorna dati Allevatore."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

    form = FormFarmer()
    if form.validate_on_submit():
        # recupero i dati e li converto in dict
        form_data = json.loads(json.dumps(request.form))
        # print("FORM_DATA_PASS:", json.dumps(form_data, indent=2))

        _id = session["id_farmer"]
        # print("USER_ID:", _id)
        farmer = Farmer.query.get(_id)
        previous_data = farmer.to_dict()
        # print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

        farmer.farmer_name = form_data["farmer_name"].strip()

        farmer.email = form_data["email"].strip()
        farmer.phone = form_data["phone"].strip()

        farmer.address = form_data["address"].strip()
        farmer.cap = form_data["cap"].strip()
        farmer.city = form_data["city"].strip()

        if form_data["affiliation_start_date"]:
            farmer.affiliation_start_date = form_data["affiliation_start_date"]

        farmer.stable_code = form_data["stable_code"].strip()
        farmer.stable_type = form_data["stable_type"].strip()
        farmer.stable_productive_orientation = form_data["stable_productive_orientation"].strip()
        farmer.stable_breeding_methods = form_data["stable_breeding_methods"].strip()

        if form_data["note_certificate"]:
            farmer.note_certificate = form_data["note_certificate"].strip()
        if form_data["note"]:
            farmer.note = form_data["note"].strip()

        print("NEW_DATA:", json.dumps(farmer.to_dict(), indent=2))

        try:
            db.session.commit()
            flash("ALLEVATORE aggiornato correttamente.")
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("farmer/farmer_update.html", form=form)

        _event = {
            "username": session["username"],
            "Modification": f"Update Farmer whit id: {_id}",
            "Previous_data": previous_data
        }
        # print("EVENT:", json.dumps(_event, indent=2))
        if event_create(_event, farmer_id=_id):
            return redirect(url_for('farmer_view_history', data=farmer.to_dict()))
        else:
            flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
            return redirect(url_for('farmer_view'))
    else:
        # recupero i dati e li converto in dict
        data = url_to_json(data)
        # print("DATA_PASS:", json.dumps(data, indent=2))

        session["id_farmer"] = data["id"]

        form.farmer_name.data = data["farmer_name"]
        form.email.data = data["email"]
        form.phone.data = data["phone"]

        form.address.data = data["address"]
        form.cap.data = data["cap"]
        form.city.data = data["city"]

        if data["affiliation_start_date"]:
            form.affiliation_start_date.data = datetime.strptime(data["affiliation_start_date"], '%Y-%m-%d')

        form.stable_code.data = data["stable_code"]
        form.stable_type.data = data["stable_type"]

        form.stable_productive_orientation.data = data["stable_productive_orientation"]
        form.stable_breeding_methods.data = data["stable_breeding_methods"]

        if data["note_certificate"]:
            form.note_certificate.data = data["note_certificate"]

        form.note.data = data["note"]

        status = data["affiliation_status"]
        if data["affiliation_end_date"]:
            end_date = data["affiliation_end_date"]
        else:
            end_date = "vuoto"
        return render_template("farmer/farmer_update.html", form=form, status=status, end_date=end_date)


@app.route("/farmer_view_history/<data>", methods=["GET", "POST"])
def farmer_view_history(data):
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

    # Elaboro i dati ricevuti
    data = url_to_json(data)
    print("DATA_PASS:", json.dumps(data, indent=2))

    # Estraggo l' ID dell'allevatore corrente
    session["id_farmer"] = data["id"]

    # Interrogo il DB
    user = Farmer.query.filter_by(id=data["id"]).first()
    _farmer = user.to_dict()
    session["user"] = _farmer

    # Estraggo la storia delle modifiche per l'utente
    history_list = user.events
    history_list = [history.to_dict() for history in history_list]
    return render_template("farmer/farmer_view_history.html", form=_farmer, history_list=history_list)


@app.route("/buyer_create/", methods=["GET", "POST"])
def buyer_create():
    """Creazione Allevatore Consorzio."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

    form = FormBuyer()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        print("FORM_DATA", json.dumps(form_data, indent=2))
        if form_data["affiliation_status"] == "NO":
            form_data["affiliation_status"] = False
        else:
            form_data["affiliation_status"] = True

        user = User.query.get(form_data["user_id"])
        user_id = user.id

        new_farmer = Buyer(
            buyer_name=form_data["buyer_name"].strip(),
            buyer_type=form_data["buyer_type"].strip(),

            email=form_data["email"].strip(),
            phone=form_data["phone"].strip(),

            address=form_data["address"].strip(),
            cap=form_data["cap"].strip(),
            city=form_data["city"].strip(),

            affiliation_start_date=form_data["affiliation_date"],
            affiliation_status=form_data["affiliation_status"],

            user_id=user_id,

            note_certificate=form_data["note_certificate"],
            note=form_data["note"]
        )
        try:
            db.session.add(new_farmer)
            db.session.commit()
            flash("ACQUIRENTE creato correttamente.")
            return redirect(url_for('buyer_view'))
        except IntegrityError as err:
            db.session.rollback()
            flash(f"ERRORE: {str(err.orig)}")
            return render_template("buyer/buyer_create.html", form=form)
    else:
        return render_template("buyer/buyer_create.html", form=form)


@app.route("/buyer_update/<data>", methods=["GET", "POST"])
def buyer_update(data):
    """Aggiorna dati Utente."""
    # Verifico autenticazione
    if not token_admin_validate():
        return redirect(url_for('logout'))

    form = FormFarmer()
    if form.validate_on_submit():
        form_data = json.loads(json.dumps(request.form))
        print("FORM_DATA_PASS:", json.dumps(form_data, indent=2))
        _id = session["id_buyer"]
        # print("USER_ID:", _id)
        valid_email = is_valid_email(form_data["email"])
        if valid_email:
            buyer = Buyer.query.get(_id)
            previous_data = buyer.to_dict()
            print("PREVIOUS_DATA", json.dumps(previous_data, indent=2))

            buyer.farmer_name = form_data["farmer_name"].strip()

            buyer.email = form_data["email"].strip()
            buyer.phone = form_data["phone"].strip()
            buyer.address = form_data["address"].strip()
            buyer.cap = form_data["cap"].strip()
            buyer.city = form_data["city"].strip()

            buyer.affiliation_date = form_data["affiliation_date"]
            buyer.affiliation_status = form_data["affiliation_status"]

            buyer.stable_code = form_data["stable_code"].strip()
            buyer.stable_type = form_data["stable_type"].strip()
            buyer.stable_productive_orientation = form_data["stable_productive_orientation"].strip()
            buyer.stable_breeding_methods = form_data["stable_breeding_methods"].strip()

            if form_data["note"] is None:
                buyer.note = "Null"
            else:
                buyer.note = form_data["note"].strip()

            print("NEW_DATA:", json.dumps(buyer.to_dict(), indent=2))

            try:
                db.session.commit()
                flash("ACQUIRENTE aggiornato correttamente.")
            except IntegrityError as err:
                db.session.rollback()
                flash(f"ERRORE: {str(err.orig)}")
                return render_template("buyer/buyer_update.html", form=form)

            _event = {
                "username": session["username"],
                "Modification": f"Update Buyer whit id: {_id}",
                "Previous_data": previous_data
            }
            # print("EVENT:", json.dumps(_event, indent=2))
            if event_create(_event, user_id=_id):
                return redirect(url_for('buyer_view'))
            else:
                flash("ERRORE creazione evento DB. Ma il record è stato modificato correttamente.")
                return redirect(url_for('buyer_view'))
        else:
            form.farmer_name.data = form_data["farmer_name"]
            form.email.data = form_data["email"]
            form.phone.data = form_data["phone"]
            form.address.data = form_data["address"]
            form.cap.data = form_data["cap"]
            form.city.data = form_data["city"]
            form.affiliation_start_date.data = form_data["affiliation_start_date"]
            form.affiliation_end_date.data = form_data["affiliation_end_date"]
            form.affiliation_status.data = form_data["affiliation_status"]
            form.stable_code.data = form_data["stable_code"]
            form.stable_type.data = form_data["stable_type"]
            form.stable_productive_orientation.data = form_data["stable_productive_orientation"]
            form.stable_breeding_methods.data = form_data["stable_breeding_methods"]
            form.note.data = form_data["note"]

            flash("ERRORE: la email inserita non è valida.")
            return render_template("buyer/buyer_update.html", form=form)
    else:
        # recupero i dati e li converto in dict
        data = url_to_json(data)
        print("DATA_PASS:", json.dumps(data, indent=2))

        session["id_buyer"] = data["id"]

        form.farmer_name.data = data["farmer_name"]
        form.email.data = data["email"]
        form.phone.data = data["phone"]
        form.address.data = data["address"]
        form.cap.data = data["cap"]
        form.city.data = data["city"]
        form.affiliation_start_date.data = data["affiliation_start_date"]
        form.affiliation_end_date.data = data["affiliation_end_date"]
        form.affiliation_status.data = data["affiliation_status"]
        form.stable_code.data = data["stable_code"]
        form.stable_type.data = data["stable_type"]
        form.stable_productive_orientation.data = data["stable_productive_orientation"]
        form.stable_breeding_methods.data = data["stable_breeding_methods"]
        form.note.data = data["note"]

        print("FORM_DATA", form.farmer_name.data)
        return render_template("buyer/buyer_update.html", form=form)
