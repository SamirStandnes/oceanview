from helpers import apology, login_required

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
#from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


@app.route("/")
def hjemmeside():
    return render_template("hjemmeside.html")

@app.route("/tjenester")
def tjenester():
    return render_template("tjenester.html")

@app.route("/bli_kunde")
def bli_kunde():
    return render_template("bli_kunde.html")

@app.route("/kontakt")
def kontakt():
    return render_template("kontakt.html")

@app.route("/meldinger", methods=["GET","POST"])
@login_required
def meldinger():

    timestamp = datetime.now()

    if request.method == "POST":
        user_id = session["user_id"]
        print(user_id)
        messages = db.execute("SELECT message_text FROM messages;")
        message = request.form['message']

        db.execute("INSERT INTO messages (sender_id, recipient_id, message_text, timestamp) VALUES (?,?,?,?);", (user_id, 1, message, timestamp))
        print(timestamp)
        print(message)
        return render_template("messages.html", messages=messages)

    else:

        #messages = db.execute("SELECT message_text FROM messages WHERE sender_id = ?;", user_id)

        return render_template("messages.html")


@app.route("/betaling", methods=["GET","POST"])
@login_required
def betaling():
    if request.method == "POST":
        return render_template("betaling.html")

    else:
        return render_template("betaling.html")




"""


@app.route("/transaksjonshistorire")
@login_required
def meldinger():

    return 0


"""



@app.route("/")
@login_required
def index():
    # Get user_id
    user_id = session["user_id"]
    username = db.execute("SELECT username FROM users WHERE id = ?;", user_id)[0]['username']
    # Render welcome message to user
    return render_template("index.html", username=username)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password don't match", 400)

        # Provided username
        username = request.form.get("username")

        # Check to see if username is available
        test_username = db.execute("SELECT username FROM users WHERE username = ?;", username)
        if test_username:
            return apology("username is taken", 400)
        # Has password
        password = generate_password_hash(request.form.get("password"))

        #email adress
        mail = request.form.get("email")

        # Create user with chosen password. Rename epost in db at some point! TO FIX
        db.execute("INSERT INTO users (username, hash, user_type, epost) VALUES(?,?,?,?);", username, password, "customer", mail)

        return redirect("/")

    else:
        return render_template("register.html")


