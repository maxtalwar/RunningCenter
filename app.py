from flask import *
from database import init_db, db_session
from models import *
from datetime import datetime
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config.from_object('config.Config')

# redirects to the login page if no path is specified in the URL
@app.route('/', methods=["GET", "POST"])
def home():
    return redirect(url_for("login"))

# logic for signup page
@app.route('/signup', methods=["GET", "POST"])
def signup():
    # if the user is already logged in, redirect them
    if "username" in session:
        return redirect(url_for("profile"))

    # if the user is just trying to see the page, render the basic template for the page without any logic
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        # if the user sends a POST request to the server, handle the signup logic

        # parse request form data
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # pull data from database
        email_exists = db_session.query(User.email).filter(User.email == email).first() is not None
        username_exists = db_session.query(User.username).filter(User.username == username).first() is not None

        # run checks against database

        # flash incorrect password error if password incorrect
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")
        # flash email already taken error if the email exists in the databse
        elif email_exists:
            flash("Email already taken.", "error")
            return render_template("signup.html")
        # flash username taken error if the username is taken
        elif username_exists:
            flash("username already taken", "error")
            return render_template("signup.html")
        # if all checks are passed, create a new user and add it to the database session
        else:
            password_hash = generate_password_hash(password)
            password = password_hash

            user = User(username=username, email=email, password=password)
            db_session.add(user)
            db_session.commit()

            #flash("Sucessfully signed up!", "info")
            
            session["username"] = username

            # redirect users to the profile page
            return redirect(url_for("profile"))

# logic for login page
@app.route('/login', methods=["GET", "POST"])
def login():
    # redirect user if they're already logged in
    if "username" in session:
        return redirect(url_for("profile"))

    # just render the page if the user isn't submitting data
    if request.method == "GET":
        return render_template("login.html")
    # handle login logic if the user is submitting data
    if request.method == "POST":
        # parse request form data
        username = request.form["username"]
        password = request.form["password"]

        # pull the corresponding user from the username
        user = db_session.query(User).filter(User.username == username).first()

        # check that the user entered a username in the database
        if user != None:
            # check that the given password is correct
            if check_password_hash(user.password, password):
                # log the user in, redirect to the profile page
                session["username"] = username

                return redirect(url_for("profile"))

    # if it ultimately fails to pass the checks throw an error and redirect back to the login page
    flash("Incorrect username or password.", "error")
    return render_template("login.html")

@app.route("/profile", defaults={"username": None})
@app.route("/profile/<username>")
def profile(username):
    logged_in_user = None

    if "username" in session:
        logged_in_user = session["username"]

    print(logged_in_user)

    # use the logged in user's username if the user doesn't specify a username in the url
    # redirect them to the login page if they're not logged in (meaning there is no session username)
    if not username:
        if logged_in_user == None:
            return redirect(url_for("login"))

        username = logged_in_user

    # get the current username, generate a user object from the given username
    user = db_session.query(User).filter(User.username == username).first()

    # if the username isn't in the database, redirect the user back to the login page.
    if user is None:
        flash("User not found. Please log in again.", "warning")
        session.pop("username", None)
        return redirect(url_for("login"))

    # get all reviews that a user left
    reviews = db_session.query(Race.race_name, Review.review_text).filter(Review.user_id == user.id).join(Race, Review.race_id == Race.id).all()

    # fill a list with strings of all the reviews and pass it to the frontend
    comments = []

    for race_name, review_text in reviews:
        comments.append(f"{race_name}: {review_text}")

    return render_template("profile.html", comments = comments, user = user, logged_in_user = logged_in_user)

@app.route("/calendar")
def calendar():
    # get all upcoming races
    races = db_session.query(Race).all()

    # calculate the average rating for each of the upcoming races, update each race object with their average rating
    for race in races:
        reviews = db_session.query(Review).filter(Review.race_id == race.id).all()

        # if reviews exist for a race, calculate average rating
        # otherwise don't calculate the average rating
        if len(reviews) > 0:
            average_rating = round(sum([review.rating for review in reviews])/len(reviews), 2)
        else:
            average_rating = "n/a"

        race.average_rating = average_rating

    # pass the updated race objects to the calendar page
    return render_template("calendar.html", races=races)

@app.route("/logout")
def logout():
    # checks if a user is logged in
    if "username" in session:
        # remove username from session, flash a logged out error
        session.pop("username")
        flash("You've been logged out", "info")

    # redirect to login page
    return redirect(url_for("login"))

@app.route('/race/<race_id>', methods=["GET", "POST"])
def race_page(race_id):
    # get data about a race that corresponds to a given race id
    race = db_session.query(Race).filter(Race.id == race_id).first()
    race_name = race.race_name

    text_reviews = (db_session.query(User, Review).filter(Review.race_id == race.id).join(User, Review.user_id == User.id).all())
    reviews = {user.username:review.review_text for (user, review) in text_reviews}

    numerical_reviews = db_session.query(Review).filter(Review.race_id == race.id).all()

    # calculate the average race rating if there are ratings for a given race
    if len(numerical_reviews) > 0:
        average_rating = round(sum([review.rating for review in numerical_reviews])/len(numerical_reviews), 1)
    else:
        average_rating = "n/a"

    # render the race page with the calculated data
    return render_template('race_page.html', race_id=race_id, race_name=race_name, average_rating=average_rating, reviews=reviews, race_description = race.race_description, race_website = race.race_website)

@app.route('/race/<int:race_id>/submit_review', methods=["POST"])
def submit_review(race_id):
    if request.method == "POST":
        # get info from the request form about the review
        rating = request.form['rating']
        comment = request.form['comment']

        # get the current logged in user, create a review text with the username at the front
        username = session.get("username")

        # check that the user is logged in, and if they're not redirect them to the singup page
        if username:
            # generate a review object based on the retrieved info about the user
            user_id = db_session.query(User.id).filter(User.username == username).first()[0]
            review_date = datetime.today().date()
            review = Review(user_id=user_id, race_id=race_id, rating=rating, review_date=review_date, review_text=comment)

            # store the review in the reviews database
            db_session.add(review)
            db_session.commit()
        else:
            flash("You must be logged in to leave a review!")
            return redirect(url_for('signup'))

    # return to the race page
    return redirect(url_for('race_page', race_id=race_id))

@app.route('/edit_profile', methods=["GET", "POST"])
def edit_profile():
    # go to the profile editor page
    return render_template('edit_profile.html')

@app.route('/save_profile_changes', methods=["POST"])
def save_profile_changes():
    if request.method == "POST":
        # figure out who is logged in
        username = session.get("username")
        user = db_session.query(User).filter(User.username == username).first()

        # change the user's bio based on the info that they give, save the changed user to the database
        altered_bio = request.form['bio']
        user.bio = altered_bio
        db_session.commit()

    # go back to the profile page
    return redirect(url_for('profile'))

if __name__ == "__main__":
    init_db()
    app.run(port=5001)
