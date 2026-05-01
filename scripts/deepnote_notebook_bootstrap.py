"""Notebook-friendly bootstrap for Apex Mentor on Deepnote/Jupyter.

Run this from a notebook cell with:

    exec(open("scripts/deepnote_notebook_bootstrap.py").read())

It installs dependencies, creates .env if needed, generates a private token, and
starts the FastAPI server in the background so the notebook cell can finish.
"""

from __future__ import annotations

import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
if ROOT.name != "Apex-Mentor" and (ROOT / "Apex-Mentor").is_dir():
    ROOT = ROOT / "Apex-Mentor"
    os.chdir(ROOT)

print(f"Using project directory: {ROOT}")

venv_dir = ROOT / ".venv"
python_bin = venv_dir / "bin" / "python"
pip_bin = venv_dir / "bin" / "pip"

if not venv_dir.exists():
    print("Creating Python virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

print("Installing dependencies...")
subprocess.run([str(python_bin), "-m", "pip", "install", "--upgrade", "pip"], check=True)
subprocess.run([str(pip_bin), "install", "-r", "requirements.txt"], check=True)

env_example = ROOT / ".env.example"
env_file = ROOT / ".env"
if not env_file.exists():
    print("Creating .env from .env.example...")
    env_file.write_text(env_example.read_text())

text = env_file.read_text()
if "change-this-token-before-exposing" in text:
    token = secrets.token_urlsafe(48)
    text = text.replace("change-this-token-before-exposing", token)
    env_file.write_text(text)
    print("Generated private APEX_AUTH_TOKEN in .env")
else:
    token = None
    for line in text.splitlines():
        if line.startswith("APEX_AUTH_TOKEN="):
            token = line.split("=", 1)[1].strip()
            break

(ROOT / "data").mkdir(exist_ok=True)

log_file = ROOT / "data" / "apex_mentor_server.log"
print("Starting Apex Mentor server in the background...")

# Stop any prior uvicorn process from this notebook session if present.
old_pid_file = ROOT / "data" / "apex_mentor_server.pid"
if old_pid_file.exists():
    try:
        old_pid = int(old_pid_file.read_text().strip())
        subprocess.run(["kill", str(old_pid)], check=False)
        time.sleep(1)
    except Exception:
        pass

with log_file.open("w") as log:
    proc = subprocess.Popen(
        [
            str(python_bin),
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
        stdout=log,
        stderr=subprocess.STDOUT,
        cwd=str(ROOT),
    )

old_pid_file.write_text(str(proc.pid))
time.sleep(3)

print("Apex Mentor is starting.")
print("Local URL: http://127.0.0.1:8000")
print("API docs: http://127.0.0.1:8000/docs")
print(f"Server log: {log_file}")
print(f"Server PID: {proc.pid}")
print("\nPrivate token from .env:")
print(token or "Could not read token from .env")
print("\nNext: expose it with Cloudflare Tunnel in another cell/terminal:")
print("cloudflared tunnel --url http://127.0.0.1:8000")
