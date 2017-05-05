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

    email_received = request.form.get('email')
    email_check = User.query.filter_by(email=email_received).all()

    if email_check == []:
        password = request.form.get('password')
        user=User(email=email_received, password=password)
        db.session.add(user)
        db.session.commit()
    return redirect("/")


@app.route('/login', methods=['GET'])
def user_login():

    print session
    return render_template("login_form.html")

@app.route('/login', methods=['POST'])
def verify_user_login():

    user_email = request.form.get('user_email')
    user_password = request.form.get('user_password')
    response = User.query.filter_by(email=user_email).all()
    if response == []:
        flash('Wrong username and/or password. Try again or Create New Account')
        return redirect("/register")
    email = response[0].email
    password = response[0].password
   # import pdb; pdb.set_trace()
    if email == user_email and password == user_password:
        session['user_email'] = request.form['user_email']
        flash('You were successfully logged in')
        return redirect("/")
    else:
        flash('Wrong username and/or password. Try again or Create New Account')
        return redirect("/register")
@app.route('/logout', methods=['POST'])
def user_logout():
#     @app.route('/logout')
# def logout():
#    # remove the username from the session if it is there
#    session.pop('username', None)
#    return redirect(url_for('index'))

    return render_template("logout_form.html")
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)
    db.session.commit()

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
