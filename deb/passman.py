"""
Start an installed PassMan. The package puts this at /usr/lib/passman and
/usr/bin/passman runs it with ``python3 -I``, so nothing from the user's own
Python setup (PYTHONPATH, ~/.local site-packages) can stand in for the
libraries the package ships.
"""

import os
import runpy
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# The program first, then the bundled libraries (customtkinter and its
# helpers); cryptography and Pillow come from the system's python3.
sys.path[:0] = [os.path.join(APP_DIR, "sourceFiles"), os.path.join(APP_DIR, "lib")]

# Tk names the window after argv[0]; "passman" ties it to passman.desktop,
# so the dock shows PassMan's icon.
sys.argv[0] = "passman"

runpy.run_path(os.path.join(APP_DIR, "sourceFiles", "gui.py"), run_name="__main__")
