from flask import *
from database import init_db, db_session
from models import *
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)

app.secret_key = "LInPyX4PpZx6hAHofg=="

@app.route('/', methods=["GET", "POST"])
def home():
    return redirect(url_for("login"))

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if "username" in session:
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        email_exists = db_session.query(User.email).filter(User.email == email).first() is not None
        username_exists = db_session.query(User.username).filter(User.username == username).first() is not None

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")
        elif email_exists:
            flash("Email already taken.", "error")
            return render_template("signup.html")
        elif username_exists:
            flash("username already taken", "error")
            return render_template("signup.html")
        else:
            user = User(username=username, email=email, password=password)
            db_session.add(user)
            db_session.commit()

            session["username"] = username

            return redirect(url_for("login"))

@app.route('/login', methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        correct_user_password = db_session.query(User.password).filter(User.username == username).first()[0]
        print("debug")

        if password == correct_user_password:
            session["username"] = username

            return redirect(url_for("profile"))
        else:
            flash("Incorrect username or password.", "error")
            print(password)
            print(correct_user_password)
            return render_template("login.html")
        
@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    user = db_session.query(User).filter(User.username == username).first()

    # if the username field is in the session data but the username doesn't exist in the actual database, this redirects the user back to the login page.
    # this is a security measure to prevent against someone setting the session username to some random value and then behind able to act as if they are logged in
    if user is None:
        flash("User not found. Please log in again.", "warning")
        session.pop("username", None)
        return redirect(url_for("login"))

    reviews = db_session.query(Race.race_name, Review.review_text).filter(Review.user_id == user.id).join(Race, Review.race_id == Race.id).all()

    comments = []

    for race_name, review_text in reviews:
        comments.append(f"{race_name}: {review_text}")

    return render_template("profile.html", username = user.username, comments=comments)

@app.route("/calendar")
def calendar():
    races = db_session.query(Race).all()
    race_data = []
    
    for race in races:
        reviews = db_session.query(Review).filter(Review.race_id == race.id).all()

        if len(reviews) > 0:
            average_rating = round(sum([review.rating for review in reviews])/len(reviews), 2)
        else:
            average_rating = "n/a"

        race.average_rating = average_rating

    return render_template("calendar.html", races=races)
        
@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username")
        flash("You've been logged out", "info")
    return redirect(url_for("login"))

@app.route('/race/<race_id>', methods=["GET", "POST"])
def race_page(race_id):
    race = db_session.query(Race).filter(Race.id == race_id).first()
    race_name = race.race_name
    reviews = db_session.query(Review).filter(Review.race_id == race.id).all()
    comments = [review.review_text for review in reviews]

    if len(reviews) > 0:
        average_rating = round(sum([review.rating for review in reviews])/len(reviews), 2)
    else:
        average_rating = "n/a"

    return render_template('race_page.html', race_id=race_id, race_name=race_name, average_rating=average_rating, comments=comments)

@app.route('/race/<int:race_id>/submit_review', methods=["POST"])
def submit_review(race_id):
    if request.method == "POST":
        print("debug 1")
        rating = request.form['rating']
        comment = request.form['comment']
        username = session.get("username")
        user_id = db_session.query(User.id).filter(User.username == username).first()[0]

        if username:
            print("debug 2")
            review = Review(user_id=user_id, race_id=race_id, rating=rating, review_date=datetime.today().strftime('%d-%d-%Y'), review_text=comment)

            db_session.add(review)
            db_session.commit()
        else:
            flash("You must be logged in to leave a review!")

    return redirect(url_for('race_page', race_id=race_id))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
