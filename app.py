from flask import *
from database import init_db, db_session
from models import *

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
    comments = db_session.query(Review.review_text).filter(Review.user_id == user.id).all()

    return render_template("profile.html", username = user.username, comments=comments)

@app.route("/calendar")
def calendar():
    return render_template("calendar.html")
        
@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username")
        flash("You've been logged out", "info")
    return redirect(url_for("login"))

@app.route('/race/<race_id>')
def race_page(race_id):
    return render_template('race_page.html', race_id=race_id)

    

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
