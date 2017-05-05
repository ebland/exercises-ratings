"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie

from bs4 import BeautifulSoup
import requests


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

    return render_template('homepage.html')


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/movies")
def show_movies():
    """Show list of movies."""

    movies = Movie.query.all()
    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<movie_id>")
def movie_details(movie_id):
    """Show details for a movie."""

    # Get movie object
    movie = Movie.query.filter_by(movie_id=movie_id).first()


    t_url = movie.imdb_url
    r = requests.get(t_url)
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')
    const_title = movie.title + ' Poster'

    thumb = [x['src'] for x in soup.findAll('img', {'alt': const_title})]


    # Get movie image
    # url = movie.imdb_url
    # r  = requests.get("http://" +url)
    # data = r.text
    # soup = BeautifulSoup(data)

    # If no movie object (user entered url for invalic movie)
    if not movie:
        movie_list = Movie.query.all()
        return render_template("movie_list.html", movies=movie_list)

    # Check if current user is logged in, get their rating
    user_id = session.get('user_id')
    if user_id:
        user_rating = Rating.query.filter_by(movie_id=movie_id,
                                             user_id=user_id).first()
    else:
        user_rating = None

    # Get average rating of movie
    rating_scores = [r.score for r in movie.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)
    prediction = None

    # Predict rating if user hasn't rated movie
    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie)

    # Evil eye stuff
    if prediction:
        effective_rating = prediction
    elif user_rating:
        effective_rating = user_rating.score
    else:
        effective_rating = None

    # Get the eye's rating, either by predicting or using real rating
    the_eye = User.query.filter_by(email='the-eye@of-judgment.com').one()
    eye_rating = Rating.query.filter_by(
        user_id=the_eye.user_id, movie_id=movie.movie_id).first()

    if eye_rating is None:
        eye_rating = the_eye.predict_rating(movie)

    else:
        eye_rating = eye_rating.score

    if eye_rating and effective_rating:
        difference = abs(eye_rating - effective_rating)

    else:
        difference = None

    # Get beratement message
    BERATEMENT_MESSAGES = [
                    "I suppose you don't have such bad taste after all.",
                    "I regret every decision that I've ever made that has " +
                    "brought me to listen to your opinion.",
                    "Words fail me, as your taste in movies has clearly " +
                    "failed you.",
                    "That movie is great. For a clown to watch. Idiot.",
                    "Words cannot express the awfulness of your taste."
    ]

    if difference is not None:
        beratement = BERATEMENT_MESSAGES[int(difference)]

    else:
        beratement = None

    return render_template("movie_details.html",
                           movie=movie,
                           ratings=movie.ratings[0:10],
                           user_rating=user_rating,
                           average=round(avg_rating, 2),
                           prediction=prediction,
                           beratement=beratement,
                           thumb=thumb[0])


@app.route('/register', methods=['GET'])
def register_user_form():
    """Shows form to register a new user"""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_user():
    """Adds new User to DB, displays success message"""

    # Get info from form
    email = request.form.get('email')
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')

    # Convert empty Int fields to None
    if age == '':
        age = None

    print email

    user = User(email=email,
                password=password,
                age=age,
                zipcode=zipcode)

    db.session.add(user)
    db.session.commit()

    return render_template("register_success.html",
                           email=email,
                           password=password,
                           age=age,
                           zipcode=zipcode)


@app.route('/check_email.json', methods=['POST'])
def check_email():

    email = request.form.get('email')

    email_check = {'email': 'free'}

    if User.query.filter_by(email=email).first():
        email_check['email'] = 'taken'

    return jsonify(email_check)


@app.route('/login', methods=['GET'])
def login_form():
    """Displays form to login a user"""

    return render_template('login_form.html')
    # return render_template('login_form_ajax.html')


@app.route('/login.json', methods=['POST'])
def verify_login():
    """Checks if user in DB, and verifies password"""

    result = {}

    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if not user:
        result['login'] = 'User not found'

    elif password == str(user.password):
        result['login'] = 'OK'

    else:
        result['login'] = 'Password does not match'

    return jsonify(result)


@app.route('/login', methods=['POST'])
def login():
    """Logs in a user"""

    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if not user:
        flash('User not found!')

    elif password == str(user.password):
        session['user_id'] = user.user_id
        flash('User: {} has been logged in!'.format(email))
        # return render_template('homepage.html')
        return redirect('/users/'+str(user.user_id))

    else:
        flash('Password does not match!')

    return render_template('login_form.html')


@app.route('/logout')
def logout():
    """Logs a user out"""

    del session['user_id']
    flash('User has been logged out')

    return render_template('homepage.html')


@app.route('/users/<user_id>')
def user_info(user_id):
    """Displays details for an individual user"""

    user = User.query.get(user_id)

    # ratings = db.session.query(Rating.score, Movie.title).join(Movie).filter(Rating.user_id == user.user_id).all()
    ratings = db.session.query(Rating.score, Movie.title).join(Movie).filter(Rating.user_id == user.user_id).all()

    return render_template('user_details.html',
                           email=user.email,
                           age=user.age,
                           zipcode=user.zipcode,
                           ratings=ratings)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
