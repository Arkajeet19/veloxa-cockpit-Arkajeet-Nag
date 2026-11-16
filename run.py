"""One command from a fresh clone, on any OS:  python run.py   (or: python run.py repl)
Creates .venv, installs 3 libraries, builds the DB from data/raw, runs the test set,
then prints the worry list and a sample answer."""
import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
PY = VENV / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")


def run(*args):
    subprocess.run([str(PY), *args], cwd=ROOT, check=True)


def main():
    if not PY.exists():
        venv.create(VENV, with_pip=True)
    run("-m", "pip", "install", "-q", "-r", "requirements.txt")
    if sys.argv[1:] == ["repl"]:
        return run("-m", "cockpit", "repl")
    run("-m", "cockpit", "build")
    tests = subprocess.run([str(PY), "-m", "cockpit", "test"], cwd=ROOT).returncode
    print("\n=== What should I worry about? ===")
    run("-m", "cockpit", "worry")
    print("\n=== Sample question ===")
    run("-m", "cockpit", "ask", "What is our ARR?")
    return tests


if __name__ == "__main__":
    sys.exit(main())
