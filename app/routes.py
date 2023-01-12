import json
from datetime import datetime
from urllib.parse import unquote

from flask import current_app as app, flash, redirect, render_template, session, url_for, jsonify

from . import forms as frms
from .app import db
from .utility import functions as fnz
from .models.accounts import Administrator


@app.route("/", methods=["GET", "POST"])
def login():
    """Go to login page."""
    form = frms.FormLogin()
    if form.validate_on_submit():
        token = fnz.admin_log_in(form)
        if token is not False:
            session["token_login"] = token
            session["user"] = form.username.data
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
            if fnz.validate_token_admin(session["token_login"]):
                pass
            else:
                return redirect(url_for('login'))
            # Estraggo l'utente amministratore corrente
            admin = Administrator.query.filter_by(username=session["user"]).first()
            _admin = admin.to_dict()
            # Estraggo la lista degli utenti amministratori
            admin_list = Administrator.query.all()
            _admin_list = [admin.to_dict() for admin in admin_list]
            return render_template("admin_view.html", admin=_admin, admin_list=_admin_list)

        except Exception as err:
            flash(f"ERROR: {err}")
            return redirect(url_for('logout'))
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('login'))


@app.route("/admin_update/<admin>", methods=["GET", "POST"])
def admin_update(admin):
    if "token_login" in session:
        try:
            if fnz.validate_token_admin(session["token_login"]):
                pass
            else:
                return redirect(url_for('login'))

        except Exception as err:
            flash(f"ERROR: {err}")
            return redirect(url_for('logout'))

        admin = json.loads(unquote(admin).replace("'", '"'))
        return render_template("admin_update.html", admin=admin)
    else:
        flash("Devi eseguire la login.")
        return redirect(url_for('login'))
