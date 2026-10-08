"""
Start the real app on a display, unlock a throwaway vault, copy a password,
and save screenshots -- the check that the unit tests cannot make.

CI runs it under a virtual display:

    xvfb-run -s "-screen 0 1280x800x24" python tools/smoke_gui.py OUT_DIR

It writes login.png and main.png to OUT_DIR and exits non-zero if a step
failed. It never touches a real vault: everything lives in a temporary
folder.

    python3 -I tools/smoke_gui.py OUT_DIR --installed

runs the copy the .deb installed in /usr/lib/passman, with its bundled
libraries, instead of the checkout, and also checks that it knows it is
installed (data in ~/.local/share/passman).
"""

import argparse
import os
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
INSTALLED_DIR = "/usr/lib/passman"

_parser = argparse.ArgumentParser()
_parser.add_argument("out_dir", nargs="?", default="smoke-out")
_parser.add_argument("--installed", action="store_true",
                     help=f"run the packaged copy in {INSTALLED_DIR}")
ARGS = _parser.parse_args()

if ARGS.installed:
    sys.path[:0] = [os.path.join(INSTALLED_DIR, "sourceFiles"),
                    os.path.join(INSTALLED_DIR, "lib")]
else:
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "sourceFiles"))

TMP = tempfile.mkdtemp(prefix="passman-smoke-")
os.environ["PASSMAN_DATA_DIR"] = os.path.join(TMP, "vault")

import customtkinter as ctk                                    # noqa: E402

import appconfig                                               # noqa: E402
import clipboard                                               # noqa: E402
import vault                                                   # noqa: E402
from gui import PasswordManagerGUI                             # noqa: E402

# config.json would otherwise land in the checkout.
appconfig.config_file = lambda: os.path.join(TMP, "config.json")

USER, PASSWORD = "demo", "correct horse battery staple"
failures = []


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        failures.append(name)


def screenshot(root, path):
    root.update()
    try:
        from PIL import ImageGrab
        ImageGrab.grab(xdisplay=os.environ.get("DISPLAY")).save(path)
        return True
    except Exception as e:                      # e.g. Pillow built without XCB
        print(f"screenshot via Pillow failed: {e}")
    return os.system(f"import -window root {path}") == 0


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    vault.create_new_user(USER, PASSWORD)
    data = vault.load_vault(PASSWORD, USER)
    for site, user in (("github.com", "alice"), ("mail.example.org", "alice@example.org"),
                       ("bank.example", "a.smith")):
        vault.add_account(data, site, user, "hunter2-" + site)
    vault.save_vault(PASSWORD, data, USER)

    root = ctk.CTk()
    app = PasswordManagerGUI(root)

    def step_login():
        check("login screenshot", screenshot(root, os.path.join(out_dir, "login.png")))
        app.username_entry.delete(0, "end")
        app.username_entry.insert(0, USER)
        app.password_entry.insert(0, PASSWORD)
        app.unlock_vault()
        root.after(2500, step_main)

    def step_main():
        check("unlocked", app.current_user == USER)
        check("main screenshot", screenshot(root, os.path.join(out_dir, "main.png")))
        app._copy("hunter2-github.com", "Password copied", sensitive=True)
        check("password on the clipboard",
              clipboard.paste(root) == "hunter2-github.com")
        app._clear_clipboard("hunter2-github.com", quiet=True)
        check("clipboard cleared", clipboard.paste(root) in ("", None))
        check("vault folder private",
              os.stat(os.environ["PASSMAN_DATA_DIR"]).st_mode & 0o777 == 0o700)
        root.after(200, root.destroy)

    def guarded(fn):
        def run():
            try:
                fn()
            except Exception:
                traceback.print_exc()
                failures.append(fn.__name__)
                root.destroy()
        return run

    step_main = guarded(step_main)
    root.after(2000, guarded(step_login))
    root.after(30000, root.destroy)              # never hang CI
    root.mainloop()
    check("reached the main window", app.current_user == USER)
    return 1 if failures else 0


def check_installed():
    """The packaged copy must find its marker and keep data in the home."""
    check("running the installed copy",
          os.path.dirname(os.path.abspath(vault.__file__))
          == os.path.join(INSTALLED_DIR, "sourceFiles"))
    check("customtkinter from the package",
          ctk.__file__.startswith(os.path.join(INSTALLED_DIR, "lib") + os.sep))
    check("knows it is installed", vault.is_installed())
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    check("data in ~/.local/share/passman",
          vault.get_home_dir() == os.path.join(base, "passman"))


if __name__ == "__main__":
    if ARGS.installed:
        check_installed()
    sys.exit(main(ARGS.out_dir))
