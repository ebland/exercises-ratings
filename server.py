"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from model import User, Ratings, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # a = jsonify([1,3])
    # return a
    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/register', methods=["GET"])
def user_register_form():
    """User registration form."""

    return render_template("register_form.html")


@app.route('/register', methods=["POST"])
def user_register_process():
    """Process for user registration."""

    email = User.email.query.all()
    email_received = request.form.get('email')
    dup_email = []

    for mail in email:
        if mail == email_received:
            dup_email.append(mail)
        else:
            email, password = Ratings.User.user_register_process(email)

    return redirect("/")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
