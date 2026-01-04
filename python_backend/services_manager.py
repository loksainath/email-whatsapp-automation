import subprocess
import sys
import os
import time
import socket

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))        # python_backend/
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))    # project root
WHATSAPP_DIR = os.path.join(ROOT_DIR, "whatsapp_server")

processes = {}

# -------------------------------------------------
# PORT CHECK (CRITICAL)
# -------------------------------------------------
def is_port_open(port: int) -> bool:
    """
    Returns True if port is already in use
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


# -------------------------------------------------
# SAFE PROCESS STARTER
# -------------------------------------------------
def start_process(name: str, cmd: str, cwd: str):
    """
    Starts a process only if not already running
    """
    if name in processes and processes[name].poll() is None:
        print(f"✔ {name} already running")
        return

    print(f"▶ Starting {name}...")

    processes[name] = subprocess.Popen(
        cmd,
        cwd=cwd,
        shell=True,                       # REQUIRED on Windows
        stdout=None,
        stderr=None,
        close_fds=False,                  # Windows safety
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )


# -------------------------------------------------
# START ALL SERVICES (SAFE & IDEMPOTENT)
# -------------------------------------------------
def start_all():

    # -------------------------------
    # 1️⃣ WhatsApp Node Server
    # -------------------------------
    if is_port_open(3000):
        print("⚠ WhatsApp already running on port 3000 — skipping start")
    else:
        start_process(
            "whatsapp",
            "node index.js",
            WHATSAPP_DIR
        )
        time.sleep(6)  # Allow QR + browser startup

    # -------------------------------
    # 2️⃣ Reply Server (WhatsApp → Gmail)
    # -------------------------------
    start_process(
        "reply_server",
        f'"{sys.executable}" reply_server.py',
        BASE_DIR
    )

    # -------------------------------
    # 3️⃣ Sender Worker (Queue → WhatsApp)
    # -------------------------------
    start_process(
        "sender_worker",
        f'"{sys.executable}" sender_worker.py',
        BASE_DIR
    )

    # -------------------------------
    # 4️⃣ Scheduler (Gmail polling)
    # -------------------------------
    start_process(
        "scheduler",
        f'"{sys.executable}" scheduler.py',
        BASE_DIR
    )

    print("✅ ALL BACKEND SERVICES STARTED")


# -------------------------------------------------
# STOP ALL SERVICES
# -------------------------------------------------
def stop_all():
    for name, proc in processes.items():
        if proc and proc.poll() is None:
            print(f"🛑 Stopping {name}")
            proc.terminate()

    processes.clear()
    print("🛑 ALL SERVICES STOPPED")
