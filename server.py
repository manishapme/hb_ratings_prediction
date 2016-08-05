"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import (User, Rating, Movie, connect_to_db, db, get_user_by_email, add_user,
                  get_user_by_email_and_password, add_rating, update_rating)


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

    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/users/<user_id>')
def user_detail(user_id):
    """Show details for one user."""

    result = User.query.get(user_id)
    return render_template('user_detail.html', user=result)
  

@app.route('/movies')
def movie_list():
    """Show list of movies."""

    #When using order_by(Classname.attribute) and .all() ALWAYS at the end
    movies = Movie.query.order_by(Movie.title).all()
    return render_template('movie_list.html', movies=movies)


@app.route('/movies/<movie_id>')
def movie_detail(movie_id):
    """Show details for one movie."""

    result = Movie.query.get(movie_id)
    return render_template('movie_detail.html', movie=result)


@app.route('/rating', methods=['POST'])
def rating_set():
    """Create or update rating for logged in user."""

    user_id = session['user_id']
    movie_id = request.form.get('movie_id')
    score = request.form.get('rating')

    result = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if result:
        flash('Your score of %s has been updated' % score)
        update_rating(user_id, movie_id, score)
    else:
        flash('Your score of %s has been added' % score)
        add_rating(user_id, movie_id, score)

    return redirect('/users/%s' % user_id)

#User.query.filter_by(email=email, password=password).first()

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Register or sign up user"""

    #post requests mean they've submitted form on register.html
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        user_age = int(request.form.get('age'))
        user_zipcode = request.form.get('zipcode')
        result = get_user_by_email(user_email) #querying DB for username

        if result:
            ##SHOW ALERT, "username exists"
            flash('That %s already exists. Please login or use a different email' % user_email)
            return redirect('/register')
        else:
            add_user(user_email, user_password, user_age, user_zipcode)
            flash('%s has been successfully registered and logged in.' % user_email)
            session['user_id'] = result.user_id
            return redirect('/')
    else:
        # coming from link on homepage.html
        return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Login existing user."""

    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        result = get_user_by_email_and_password(user_email, user_password)

        if result:
            flash('Hello %s, you are logged in' % user_email)
            session['user_id'] = result.user_id
            return redirect('/users/%s' % result.user_id)
        else:
            flash('Error, %s and password did not match a registered user' % user_email)
            return redirect('/login')    

    else:
        return render_template('login.html')


@app.route('/logout')
def logout_user():
    """logout user"""

    flash('Logged out')
    del session['user_id']

    return redirect('/')        



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
