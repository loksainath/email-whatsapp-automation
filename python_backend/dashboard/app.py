# from flask import Flask, render_template, jsonify, Response
# import json
# import os
# import csv

# app = Flask(__name__)

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_DIR = os.path.dirname(BASE_DIR)

# EMAIL_LOG = os.path.join(PROJECT_DIR, "email_logs.json")
# QUEUE_FILE = os.path.join(PROJECT_DIR, "message_queue.json")


# def load_json_safe(path, default):
#     try:
#         if os.path.exists(path):
#             with open(path, "r", encoding="utf-8") as f:
#                 data = json.load(f)
#                 return data if isinstance(data, list) else default
#     except Exception:
#         pass
#     return default


# @app.route("/")
# def home():
#     return render_template("index.html")


# @app.route("/api/analytics")
# def analytics():
#     emails = load_json_safe(EMAIL_LOG, [])
#     queue = load_json_safe(QUEUE_FILE, [])

#     priority_count = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
#     replied = 0

#     for e in emails:
#         p = e.get("priority", "LOW")
#         priority_count[p] = priority_count.get(p, 0) + 1
#         if e.get("status") == "Replied":
#             replied += 1

#     return jsonify({
#         "total_emails": len(emails),
#         "queued_messages": len(queue),
#         "replies": replied,
#         "priority": priority_count
#     })


# @app.route("/api/logs")
# def logs():
#     emails = load_json_safe(EMAIL_LOG, [])
#     return jsonify(emails[-100:])


# @app.route("/download/logs")
# def download_logs():
#     emails = load_json_safe(EMAIL_LOG, [])

#     def generate():
#         yield "From,Subject,Priority,Status,Time\n"
#         for e in emails:
#             yield f"{e.get('from','')},{e.get('subject','')},{e.get('priority','')},{e.get('status','')},{e.get('time','')}\n"

#     return Response(
#         generate(),
#         mimetype="text/csv",
#         headers={"Content-Disposition": "attachment;filename=email_logs.csv"}
#     )


# if __name__ == "__main__":
#     app.run(port=7000, debug=False)


import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, request, redirect, session
from auth import register_user, authenticate_user, get_user, update_profile
from session_config import configure_session

app = Flask(__name__)
configure_session(app)

# =========================================
# HOME
# =========================================
@app.route("/")
def home():
    return redirect("/login")


# =========================================
# REGISTER
# =========================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        ok = register_user(
            full_name=request.form["full_name"],
            email=request.form["email"],
            password=request.form["password"]
        )

        if ok:
            return redirect("/login")

        return render_template(
            "register.html",
            error="User already exists"
        )

    return render_template("register.html")


# =========================================
# LOGIN
# =========================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uid = authenticate_user(
            request.form["email"],
            request.form["password"]
        )

        if not uid:
            return render_template(
                "login.html",
                error="Invalid credentials"
            )

        session.clear()
        session["user_id"] = uid

        # ---------------------------------
        # CHECK PROFILE COMPLETENESS
        # ---------------------------------
        user = get_user(uid)

        # DB schema order (IMPORTANT):
        # 0 full_name
        # 1 email
        # 2 gmail_email
        # 3 gmail_app_password
        # 4 whatsapp
        # 5 language
        # 6 role
        # 7 created_at

        gmail_email = user[2]
        gmail_app_password = user[3]
        whatsapp_number = user[4]

        # Force profile completion
        if not gmail_email or not gmail_app_password or not whatsapp_number:
            return redirect("/profile")

        # Profile complete → Dashboard
        return redirect("http://127.0.0.1:7000/")

    return render_template("login.html")


# =========================================
# PROFILE (MANDATORY)
# =========================================
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]

    if request.method == "POST":
        update_profile(
            user_id=uid,
            gmail_email=request.form["gmail_email"],
            gmail_app_password=request.form["gmail_app_password"],
            whatsapp=request.form["whatsapp"],
            language=request.form.get("language", "English")
        )

        # After profile save → dashboard
        return redirect("http://127.0.0.1:7000/waiting")


    user = get_user(uid)
    return render_template("profile.html", user=user)


# =========================================
if __name__ == "__main__":
    print("🔐 Auth server running on http://127.0.0.1:5001")
    app.run(port=5001, debug=False)
