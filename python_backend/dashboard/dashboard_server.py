import sys
import os
import json
import subprocess
import requests
import threading

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, redirect, session, jsonify
from flask_socketio import SocketIO
from functools import wraps

from state_manager import set_socketio

# =================================================
# APP SETUP
# =================================================
app = Flask(__name__)
app.secret_key = "dashboard-secret-key"

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

set_socketio(socketio)

# =================================================
# PATHS
# =================================================
DASHBOARD_DIR = os.path.dirname(__file__)
PY_BACKEND_DIR = os.path.abspath(os.path.join(DASHBOARD_DIR, ".."))
ROOT_DIR = os.path.abspath(os.path.join(DASHBOARD_DIR, "../.."))

LOG_FILE = os.path.join(PY_BACKEND_DIR, "email_logs.json")

WHATSAPP_DIR = os.path.join(ROOT_DIR, "whatsapp_server")
WHATSAPP_READY_URL = "http://127.0.0.1:3000/ready"

# =================================================
# RUNTIME FLAGS (MEMORY ONLY — CORRECT WAY)
# =================================================
whatsapp_process = None
backend_started = False
backend_lock = threading.Lock()

# =================================================
# AUTH GUARD
# =================================================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("http://127.0.0.1:5001/login")
        return f(*args, **kwargs)
    return wrapper

# =================================================
# ROUTES
# =================================================
@app.route("/")
@login_required
def dashboard():
    return render_template("index.html")

@app.route("/profile")
@login_required
def profile():
    return redirect("http://127.0.0.1:5001/profile")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("http://127.0.0.1:5001/login")

# =================================================
# WHATSAPP QR WAIT PAGE
# =================================================
@app.route("/waiting")
@login_required
def waiting():
    global whatsapp_process

    if whatsapp_process is None or whatsapp_process.poll() is not None:
        print("🚀 Launching WhatsApp Chromium")

        whatsapp_process = subprocess.Popen(
            ["node", "index.js"],
            cwd=WHATSAPP_DIR,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            if sys.platform.startswith("win") else 0
        )

    return """
    <h2>📱 Scan WhatsApp QR Code</h2>
    <p>Waiting for WhatsApp to be ready...</p>
    <script>
      setInterval(() => {
        fetch("/check-whatsapp")
          .then(r => r.json())
          .then(d => {
            if (d.ready) location.href = "/";
          });
      }, 2000);
    </script>
    """

# =================================================
# WHATSAPP READY CHECK + BACKEND START (FIXED)
# =================================================
@app.route("/check-whatsapp")
@login_required
def check_whatsapp():
    global backend_started

    try:
        ready = requests.get(
            WHATSAPP_READY_URL,
            timeout=2
        ).status_code == 200
    except Exception:
        ready = False

    if ready:
        with backend_lock:
            if not backend_started:
                print("▶ WhatsApp READY → starting backend services")

                subprocess.Popen(
                    [sys.executable, "python_backend/reply_server.py"],
                    cwd=ROOT_DIR
                )

                subprocess.Popen(
                    [sys.executable, "python_backend/sender_worker.py"],
                    cwd=ROOT_DIR
                )

                subprocess.Popen(
                    [sys.executable, "python_backend/main.py"],
                    cwd=ROOT_DIR
                )

                backend_started = True
                print("🎉 Backend started successfully")

    return jsonify({"ready": ready})

# =================================================
# DASHBOARD DATA API (FALLBACK)
# =================================================
@app.route("/api/data")
@login_required
def api_data():
    if not os.path.exists(LOG_FILE):
        return jsonify([])

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        print("❌ Dashboard API error:", e)
        return jsonify([])

# =================================================
# RUN SERVER
# =================================================
if __name__ == "__main__":
    print("📊 Dashboard running on http://127.0.0.1:7000")
    socketio.run(
        app,
        host="127.0.0.1",
        port=7000,
        debug=False,
        allow_unsafe_werkzeug=True
    )
