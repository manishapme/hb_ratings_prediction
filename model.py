"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
import correlation

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)
        
    def similarity(self, other):
        """Return Pearson rating for user compared to other user."""

        u_ratings = {}
        paired_ratings = []

        for r in self.ratings:
            u_ratings[r.movie_id] = r

        for o_r in other.ratings:
            u_r = u_ratings.get(o_r.movie_id)
            if u_r:
                paired_ratings.append( (u_r.score, o_r.score))

        if paired_ratings:
            return correlation.pearson(paired_ratings)
        else:
            return 0.0


    def make_a_prediction(self, movie):
        """Finds the user with the highest similarity coefficent 
            given movie"""

        # returns a list of rating objects
        other_ratings = movie.ratings
        #Find other people who's rated this movie
        other_users = [r.user for r in other_ratings]

        users = [(self.similarity(other_u), other_u)
            for other_u in other_users 
            if other_u is not self
            ]

        sorted_users = sorted(users, reverse=True)
        sim, best_match_user = sorted_users[0]

        for rating in other_ratings:
            if rating.user_id == best_match_user.user_id:
                print sim, best_match_user
                return rating.score * sim 
                    

        
# Put your Movie and Rating model classes here.
class Movie(db.Model):
    """Information about individual movie"""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Movie movie_id=%s title=%s>" % (self.movie_id, self.title)



class Rating(db.Model):
    """The rating a user entered for a specific movie."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer, nullable=False)

    #define relationships
    user = db.relationship("User", backref=db.backref("ratings", order_by=rating_id))
    movie = db.relationship("Movie", backref=db.backref("ratings", order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        s = "<Rating rating_id=%s movie_id=%s user_id=%s score=%s>"
        return s % (self.rating_id, self.movie_id, self.user_id, self.score)


##############################################################################
# Add, update, delete functions

def add_user(email, password, age=None, zipcode=""):
    """Add new user"""

    user = User(email=email,
                password=password,
                age=age,
                zipcode=zipcode)

    db.session.add(user)   
    db.session.commit()   


def update_rating(user_id, movie_id, score):
    """Update existing rating"""

     # alternate style of update. Note update({}) requires a dictionary be passed as argument
     # rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).update({'score': score})
    rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    rating.score = score
    db.session.commit()

    return rating


def add_rating(user_id, movie_id, score):
    """Add a new rating"""
    rating = Rating(user_id=user_id,
                         movie_id=movie_id,
                         score=score)

    db.session.add(rating)
    db.session.commit()


##############################################################################
# Query functions

def get_user_by_email(email):
    """Show information about one user."""

    user = User.query.filter_by(email=email).first()
    return user


def get_user_by_email_and_password(email, password):
    """Verify email and password match stored credentials."""

    user = User.query.filter_by(email=email, password=password).first()

    return user


              


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
