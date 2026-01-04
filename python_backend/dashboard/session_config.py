import os
from flask_session import Session

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SESSION_DIR = os.path.join(BASE_DIR, "_shared_session")

def configure_session(app):
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = SESSION_DIR
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_COOKIE_NAME"] = "email_whatsapp_session"
    app.config["SESSION_COOKIE_PATH"] = "/"
    app.config["SECRET_KEY"] = "email-whatsapp-shared-secret"

    os.makedirs(SESSION_DIR, exist_ok=True)
    Session(app)
