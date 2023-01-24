from flask import current_app as app, flash, redirect, render_template, session, url_for

from ..forms.forms import FormLogin
from ..utilitys.functions import admin_log_in


@app.route("/", methods=["GET", "POST"])
def login():
    """Effettua la log-in."""
    form = FormLogin()
    if form.validate_on_submit():
        # print(f"USER: {form.username.data}; PSW: {form.password.data}")
        token = admin_log_in(form)
        if token:
            session["token_login"] = token
            session["username"] = form.username.data
            return redirect(url_for('cert_cons_view'))
        else:
            flash("Invalid username or password. Please try again!", category="alert")
            return render_template("login.html", form=form)
    else:
        return render_template("login.html", form=form)


@app.route("/logout/")
def logout():
    """Effettua il log-out ed elimina i dati della sessione."""
    session.clear()
    flash("Log-Out effettuato.")
    return redirect(url_for('login'))
