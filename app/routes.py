from flask import current_app as app
from flask import flash, redirect, render_template, session, url_for

from . import forms as frms
from .utility import functions as fnz


@app.route("/", methods=["GET", "POST"])
def login():
	"""Go to login page."""
	form = frms.LoginForm()
	if form.validate_on_submit():
		token = fnz.admin_log_in(form)
		if token is not False:
			session["syd_token"] = token
			# return redirect(url_for('account'))
			flash(f"Login OK.")
			return redirect(url_for('login'))
		else:
			flash("Invalid username or password. Please try again!", category="alert")
			return render_template("login.html", form=form)
	else:
		flash("Invalid username or password. Please try again!")
		return render_template("login.html", form=form)
