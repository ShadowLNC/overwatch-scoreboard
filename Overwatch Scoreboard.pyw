import os
import venv
import subprocess

created = False
if not os.path.isdir("venv"):
    created = True
    venv.create("venv", with_pip=True)  # Create venv.

path = "venv/bin/"
if not os.path.isdir(path):
    path = "venv/Scripts/"

if created:
    # pip can't run properly if not in a shell so we have to do python -m pip.
    subprocess.run([path + "python", "-m", "pip",
                    "install", "-r", "requirements.txt"])

# Alternatively set stderr=subprocess.DEVNULL but this breaks Ctrl-C (why?)
os.environ['KIVY_NO_CONSOLELOG'] = '1'
subprocess.run([path + "pythonw", "scoreboard.py"])
