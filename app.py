# import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, formulate_message, send_telegram_message

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///mle.db")

# # Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():

    # Get data
    index = db.execute("SELECT * FROM colis WHERE user_id = :user_id", user_id=session["user_id"])

    # Reverse list to get recent first
    index.reverse()

    return render_template("index.html", index=index)

@app.route("/ajouter", methods=["GET", "POST"])
@login_required
def add():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        colis_code = request.form.get("colis_code")
        phone = request.form.get("phone")
        etat = request.form.get("etat")
        city = request.form.get("city")
        price = request.form.get("price")
        
        # check
        something_is_missing = not (colis_code and phone and etat and city and price)
        if something_is_missing:
            return apology("chi 7aja na9sa", 403)

        # add to database
        db.execute("INSERT INTO colis (user_id, code, price, costumer_phone, store_name, etat, status, city) VALUES (:user_id, :code, :price, :phone, 'MAGASA', :etat, 'Nouveau Colis', :city)",
                   user_id=session["user_id"], code=colis_code, phone=phone, etat=etat, city=city, price=price)

        # Redirect user to index
        flash("Ajoutée avec succès")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("ajouter.html")

@app.route("/changer", methods=["GET", "POST"])
@login_required
def change():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        colis_code = request.form.get("code")
        etat = request.form.get("etat")
        status = request.form.get("status")
        
        # check
        something_is_missing = not (colis_code and etat and status)
        if something_is_missing:
            return apology("chi 7aja na9sa", 403)

        # update database
        db.execute("UPDATE colis SET status = :status, etat = :etat WHERE user_id = :user_id AND code = :code", code=colis_code, user_id=session["user_id"], etat=etat, status=status)

        # Send message if recieved
        if ('Ramassé' in status):
            # Get colis from database
            colis = db.execute("SELECT * FROM colis WHERE user_id = :user_id AND code = :code", code=colis_code, user_id=session["user_id"])
            city = colis[0]["city"]
            phone = colis[0]["costumer_phone"]

            # Send message
            message = formulate_message(colis_code, city, phone)
            send_telegram_message('1696949539', message)
        
        # Redirect user to index
        flash("Changée avec succès")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get data
        index = db.execute("SELECT * FROM colis WHERE user_id = :user_id", user_id=session["user_id"])

        # Reverse list to get recent first
        index.reverse()

        # Get page
        return render_template("changer.html", index=index)

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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

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

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure username was submitted
        if not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure confirmation was submitted
        if not request.form.get("confirmation"):
            return apology("must confirm password", 403)

        # Ensure password confirmation is correct
        if not request.form.get("confirmation") == request.form.get("password"):
            return apology("paswords don't match")

        # Ensure username does not already exist
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        if len(rows) != 0:
            return apology("Username already exists, please change it.")

        # Register new user
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :password_hash)",
                   username=request.form.get("username"), password_hash=generate_password_hash(request.form.get("password")))

        # Log user in
        user_id = db.execute("SELECT id FROM users WHERE username = :username", username=request.form.get("username"))
        session["user_id"] = user_id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# if __name__ == '__main__':
#     app.debug = True
#     app.run(host='0.0.0.0', port= 5000)