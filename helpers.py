import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", code=code, error=message)


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

import requests
from datetime import datetime, timedelta, date

def formulate_message(code, city, phone):
    # Check if Casablanca
    is_casablanca = city == 'Casablanca'

    # Define date of delivery
    date = str(datetime.date(datetime.today())) if is_casablanca else str(datetime.date(datetime.today() + timedelta(days=1)))
    year = date[0:4]
    month = date[5:7]
    day = date[8:]
    date_of_delivery = day + '-' + month + '-' + year
    # formulate the message
    message = f"Message à {phone}:\n" + f"Votre colis {code} sera livré dans la journée du {date_of_delivery}. MLExpress vous remercie pour votre fidélité."

    # return the message
    return message

# Function that sends massage to telegram
def send_telegram_message(chat_id, msg):
    url_rqst = "https://api.telegram.org/bot1738324913:AAF_0mdg89smDteKBrIAceQrESULYOzx6aY" + "/sendMessage?chat_id=" + chat_id + "&text=" + msg
    result = requests.get(url_rqst)