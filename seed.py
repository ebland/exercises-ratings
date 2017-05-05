"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User
from model import Rating
from model import Movie
import datetime

from model import connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()

    #Also add the Judgmental Eye
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    eye = User(user_id=max_id+1, email="the-eye@of-judgment.com", password="evil")
    db.session.add(eye)
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    Movie.query.delete()

    for row in open("seed_data/u.item"):
        row = row.rstrip().split('|')
        movie_id, title, released_at, imdb_url = row[0], row[1], row[2], row[4]

        if released_at == '':
            released_at = None
        else:
            released_at = datetime.datetime.strptime(released_at, "%d-%b-%Y")

        movie = Movie(movie_id=int(movie_id),
                      title=title[0:-7],
                      released_at=released_at,
                      imdb_url=imdb_url)

        db.session.add(movie)

    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""

    Rating.query.delete()

    for row in open("seed_data/u.data"):
        row = row.rstrip().split('\t')
        user_id, movie_id, score = row[0], row[1], row[2]

        rating = Rating(movie_id=int(movie_id),
                        user_id=int(user_id),
                        score=int(score))

        db.session.add(rating)

    db.session.commit()

    #Add Judgmental Eye's ratings too
    eye = User.query.filter(User.email == "the-eye@of-judgment.com").one()

    # Toy Story
    r = Rating(user_id=eye.user_id, movie_id=1, score=1)
    db.session.add(r)

    # Robocop 3
    r = Rating(user_id=eye.user_id, movie_id=1274, score=5)
    db.session.add(r)

    # Judge Dredd
    r = Rating(user_id=eye.user_id, movie_id=373, score=5)
    db.session.add(r)

    # 3 Ninjas
    r = Rating(user_id=eye.user_id, movie_id=314, score=5)
    db.session.add(r)

    # Aladdin
    r = Rating(user_id=eye.user_id, movie_id=95, score=1)
    db.session.add(r)

    # The Lion King
    r = Rating(user_id=eye.user_id, movie_id=71, score=1)
    db.session.add(r)

    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
