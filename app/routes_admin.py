import json
from datetime import datetime
from urllib.parse import unquote
from psycopg2.extras import Json

from flask import current_app as app, flash, redirect, render_template, session, url_for, jsonify, request

from . import forms as frms
from .app import db
from .utility import functions as fnz
from .utility.functions_accounts import is_valid_email
from .utility.psw_function import psw_contain_usr, psw_verify, psw_hash
from .utility.functions import event_create
from .models.accounts import Administrator


@app.route("/", methods=["GET", "POST"])
def login():
    """Go to login page."""
    form = frms.FormLogin()
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
    try:
        session.pop("token_login", None)
        session.pop("user", None)
        session.pop("admin", None)
        flash("Logout effettuato. Effettua la login se vuoi proseguire...", category="info")
        return redirect(url_for('login'))
    except ValueError:
        flash("Logout effettuato. Effettua la login se vuoi proseguire...", category="info")
        return redirect(url_for('login'))


@app.route("/admin_view/", methods=["GET", "POST"])
def admin_view():
    """Visualizzo informazioni Administrator."""
    if "token_login" in session:
        try:
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

        except Exception as err:
            flash(f"ERROR: {err}")
            return redirect(url_for('logout'))
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('login'))


@app.route("/admin_update/", methods=["GET", "POST"])
def admin_update():
    if "token_login" in session:
        if fnz.token_admin_validate(session["token_login"]):
            pass
        else:
            return redirect(url_for('login'))

        form = frms.AccountUpdateForm()
        if request.method == "POST":
            form_data = json.loads(json.dumps(request.form))
            # print("FORM_DATA", json.dumps(form_data, indent=2))
            try:
                _admin = json.loads(json.dumps(session["admin"]))
                # print("SESSION_ADMIN:", _admin["id"])
                valid_email = is_valid_email(form_data["email"])
                if valid_email:
                    administrator = Administrator.query.get(_admin["id"])
                    previus_data = administrator.to_dict()

                    administrator.username = form_data["username"]
                    administrator.name = form_data["name"]
                    administrator.last_name = form_data["last_name"]
                    administrator.email = form_data["email"]
                    administrator.updated_at = datetime.now()

                    db.session.commit()

                    _event = {
                        "username": session["username"],
                        "Modification": f"Update account administrator whit id: {_admin['id']}",
                        "Previous_data": previus_data
                    }
                    if event_create(_event, admin_id=_admin['id']):
                        return redirect(url_for('admin/admin_view'))
                    else:
                        flash("ERROR CREATE EVENT BD. But the record changes were done.")
                        return redirect(url_for('admin/admin_view'))
                else:
                    form.username.data = form_data["username"]
                    form.email.data = form_data["email"]
                    form.name.data = form_data["name"]
                    form.last_name.data = form_data["last_name"]

                    flash("ERROR: the email is not a valid email.")
                    return render_template("admin/admin_update.html", form=form)
            except Exception as err:
                flash("ERROR:", err)
                return render_template("admin/admin_update.html", form=form)
        else:
            form = frms.AccountUpdateForm()
            admin = session["admin"]
            form.username.data = admin["username"]
            form.email.data = admin["email"]
            form.name.data = admin["name"]
            form.last_name.data = admin["last_name"]
            print(form.username.data)
            return render_template("admin/admin_update.html", form=form)
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('login'))


@app.route("/admin_update_password/", methods=["GET", "POST"])
def admin_update_password():
    if "token_login" in session:
        if fnz.token_admin_validate(session["token_login"]):
            pass
        else:
            return redirect(url_for('logout'))

        form = frms.PswChangeForm()
        if form.validate_on_submit():
            form_data = json.loads(json.dumps(request.form))
            _admin = json.loads(json.dumps(session["admin"]))

            verify_password = psw_verify(form_data["new_password_1"])
            if verify_password is not False:
                message = json.loads(json.dumps(verify_password))
                flash(f"PASSWORD_WEAK:")
                flash(message)
                return render_template("admin_update_password.html", form=form)

            contain_usr = psw_contain_usr(form_data["new_password_1"], _admin["username"])
            if contain_usr is not False:
                message = json.loads(json.dumps(contain_usr))
                flash(f"PASSWORD_CONTAIN_USER:")
                flash(message)
                return render_template("admin_update_password.html", form=form)

            try:
                old_password = psw_hash(form_data["old_password"])
                # print("OLD:", old_password)
                new_password = psw_hash(form_data["new_password_1"])
                # print("NEW:", new_password)
                administrator = Administrator.query.get(_admin["id"])
                if new_password == administrator.password:
                    flash("The 'New Password' inserted is equal to 'Registered Password'.")
                    return render_template("admin_update_password.html", form=form)
                elif old_password != administrator.password:
                    flash("The 'Current Passwort' inserted does not match the 'Registered Password'.")
                    return render_template("admin_update_password.html", form=form)
                else:
                    administrator.password = new_password
                    administrator.updated_at = datetime.now()
                    db.session.commit()
                    flash("Password update correctly!")
                    try:
                        # registro modifica in eventi DB
                        _event = {
                            "User": session["username"],
                            "Modification": "Change Password"
                        }
                        if event_create(_event, admin_id=_admin["id"]):
                            return redirect(url_for('admin_view'))
                        else:
                            flash("ERROR CREATE EVENT. But your password is changed.")
                            return redirect(url_for('admin/admin_view'))
                    except Exception as err:
                        flash("ERROR_REGISTR_EVENT:", err)
                        flash("ATTENZIONE: la password è stata aggiornata. Utilizza quella nuova")
                        return render_template("admin/admin_update_password.html", form=form)
            except Exception as err:
                flash("ERROR:", err)
                return render_template("admin/admin_update_password.html", form=form)
        else:
            return render_template("admin/admin_update_password.html", form=form)
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('logout'))


@app.route("/admin_view_history/", methods=["GET", "POST"])
def admin_view_history():
    """Visualizzo la storia delle modifiche al record utente Administrator."""
    if "token_login" in session:
        try:
            if fnz.token_admin_validate(session["token_login"]):
                pass
            else:
                return redirect(url_for('login'))
            # Estraggo l'utente amministratore corrente
            admin = Administrator.query.filter_by(username=session["username"]).first()
            _admin = admin.to_dict()
            session["admin"] = _admin
            # Estraggo la storia delle modifiche per l'utente
            history_list = admin.event
            history_list = [history.to_dict() for history in history_list]
            return render_template("admin/admin_view_history.html", admin=_admin, history_list=history_list)

        except Exception as err:
            flash(f"ERROR: {err}")
            return redirect(url_for('logout'))
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('logout'))
