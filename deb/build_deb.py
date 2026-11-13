"""
Build the SecretSpace .deb on Debian or Ubuntu:

    python3 deb/build_deb.py

writes build/secretspace_<version>_all.deb. Install it with

    sudo apt install ./build/secretspace_<version>_all.deb

Needs dpkg-deb (every Debian and Ubuntu has it) and pip, which fetches the
libraries listed in deb/vendor.txt. Nothing is installed on the build
machine.

What the package holds:

    /usr/bin/secretspace                 starts the app (python3 -I)
    /usr/lib/secretspace/secretspace.py      the launcher behind it
    /usr/lib/secretspace/sourceFiles/    the program, without its tests
    /usr/lib/secretspace/lib/            customtkinter, darkdetect, packaging
    /usr/lib/secretspace/installed       the marker: data lives in
                                     ~/.local/share/secretspace, not here
    /usr/share/applications/secretspace.desktop
    /usr/share/icons/hicolor/512x512/apps/secretspace.png

cryptography, Pillow and Tk come from Ubuntu (DEPENDS), so the package is
Architecture: all and keeps working when the system's python3 is upgraded.
"""

import argparse
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOURCE_DIR = os.path.join(ROOT, "sourceFiles")
VENDOR_FILE = os.path.join(HERE, "vendor.txt")

PACKAGE = "secretspace"
#: The package name before the rename (0.9.0 and 1.0.0~alpha.1).
OLD_PACKAGE = "passman"
APP_DIR = "/usr/lib/secretspace"
MAINTAINER = "usermaneGermane <scoop-shabby-wad@duck.com>"
HOMEPAGE = "https://github.com/usermaneGermane/SecretSpace-Client-Linux"

#: Ubuntu 22.04 ships Python 3.10, the oldest the app supports.
#: python3-pil.imagetk is separate from python3-pil on Debian and
#: customtkinter's images need it.
DEPENDS = [
    "python3 (>= 3.10)",
    "python3-tk",
    "python3-cryptography",
    # Argon2id for 3.0 accounts: Ubuntu's python3-cryptography (3.4 on
    # 22.04, 41 on 24.04) predates it. In universe on both.
    "python3-argon2",
    "python3-pil",
    "python3-pil.imagetk",
    "fonts-dejavu-core",
]

#: Files of sourceFiles/ that go into the package; the tests stay behind.
#: The typeface (Manrope) travels with the program, licence beside it.
SOURCE_PATTERNS = (".py", ".png", ".ttf", "-OFL.txt")

LAUNCHER = f"""#!/bin/sh
# -I: the user's PYTHONPATH and ~/.local packages must not replace the
# libraries in {APP_DIR}/lib.
exec /usr/bin/python3 -I {APP_DIR}/secretspace.py "$@"
"""

DESKTOP_ENTRY = """[Desktop Entry]
Type=Application
Name=SecretSpace
GenericName=Password Manager
Comment=A local, encrypted password manager
Exec=secretspace
Icon=secretspace
Terminal=false
Categories=Utility;
Keywords=password;vault;login;
StartupWMClass=secretspace
"""

# The program folder is not writable by the user, so the app cannot leave
# __pycache__ there itself. Compile at install and remove the result before
# removal, as Debian's own Python packages do.
POSTINST = f"""#!/bin/sh
set -e
if [ "$1" = configure ] && command -v py3compile >/dev/null 2>&1; then
    py3compile -p {PACKAGE} {APP_DIR} || true
fi
"""

PRERM = f"""#!/bin/sh
set -e
if command -v py3clean >/dev/null 2>&1; then
    py3clean -p {PACKAGE} || true
fi
find {APP_DIR} -depth -type d -name __pycache__ -exec rm -rf {{}} + 2>/dev/null || true
"""

MARKER_TEXT = """\
Installed by the secretspace package. Because this file exists, SecretSpace keeps
its vaults and settings in ~/.local/share/secretspace (or $XDG_DATA_HOME/secretspace)
and never in this folder. Removing the package leaves them in place.
"""


def read_version(source_dir=SOURCE_DIR):
    with open(os.path.join(source_dir, "version.py"), encoding="utf-8") as f:
        match = re.search(r'^__version__\s*=\s*"([^"]+)"', f.read(), re.M)
    if not match:
        raise SystemExit("no __version__ in version.py")
    return match.group(1)


def deb_version(version: str) -> str:
    """
    The package's Version. In Debian a hyphen starts the package revision,
    so 1.0.0-alpha.1 would sort *after* 1.0.0; a tilde sorts before
    anything, so 1.0.0~alpha.1 comes after 0.9.0 and before 1.0.0.
    """
    return version.replace("-", "~", 1)


def vendored(vendor_file=VENDOR_FILE):
    """(name, version) pairs pinned in vendor.txt."""
    pins = []
    with open(vendor_file, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                name, version = line.split()[0].split("==")
                pins.append((name, version))
    return pins


def control(version, installed_size_kb):
    return (
        f"Package: {PACKAGE}\n"
        f"Version: {version}\n"
        "Architecture: all\n"
        f"Maintainer: {MAINTAINER}\n"
        f"Installed-Size: {installed_size_kb}\n"
        f"Depends: {', '.join(DEPENDS)}\n"
        # The package was called passman before the rename to SecretSpace.
        # Installing this one removes that one in the same step; the vaults
        # in the user's home are not part of either package and stay put.
        f"Conflicts: {OLD_PACKAGE}\n"
        f"Replaces: {OLD_PACKAGE}\n"
        f"Provides: {OLD_PACKAGE}\n"
        "Section: utils\n"
        "Priority: optional\n"
        f"Homepage: {HOMEPAGE}\n"
        "Description: local, encrypted password manager\n"
        " SecretSpace keeps your logins in a single AES-256-GCM encrypted vault\n"
        " file. It works offline, with no account; two PCs can stay in step\n"
        " through a sync server you run yourself. Vaults move unchanged\n"
        " between SecretSpace for Windows and for Linux.\n"
    )


def copyright_text(pins):
    bundled = "\n".join(f"   {name} {version}" for name, version in pins)
    return f"""\
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: SecretSpace
Source: {HOMEPAGE}

Files: *
Copyright: usermaneGermane
License: GPL-3.0-only
 SecretSpace is free software under the GNU General Public License,
 version 3 only. On Debian systems its text is in
 /usr/share/common-licenses/GPL-3.

Files: usr/lib/secretspace/sourceFiles/Manrope-*.ttf
Copyright: 2018 The Manrope Project Authors
License: OFL-1.1
 The SIL Open Font License, version 1.1; its text is in
 /usr/lib/secretspace/sourceFiles/Manrope-OFL.txt.

Files: usr/lib/secretspace/lib/*
Comment: bundled Python libraries; each one's licence is in its
 *.dist-info folder next to it:
{bundled}
"""


def write(path, text, mode=0o644):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.chmod(path, mode)


def fetch_wheels(dest, vendor_file=VENDOR_FILE):
    """Download the wheels pinned in vendor.txt; pip checks every hash."""
    subprocess.run(
        [sys.executable, "-m", "pip", "download", "--quiet", "--no-deps",
         "--only-binary", ":all:", "--require-hashes",
         "-r", vendor_file, "-d", dest],
        check=True)
    wheels = sorted(os.path.join(dest, n) for n in os.listdir(dest) if n.endswith(".whl"))
    for wheel in wheels:
        if not wheel.endswith("-py3-none-any.whl"):
            raise SystemExit(f"not a pure-Python wheel: {os.path.basename(wheel)}")
    return wheels


def unpack_wheels(wheels, lib_dir):
    """A pure-Python wheel installs by unpacking it; that is all pip does."""
    os.makedirs(lib_dir, exist_ok=True)
    for wheel in wheels:
        with zipfile.ZipFile(wheel) as z:
            z.extractall(lib_dir)


def stage(tree, version, wheels, source_dir=SOURCE_DIR, pins=()):
    """Lay out the package's files under ``tree`` (the future /)."""
    app = os.path.join(tree, APP_DIR.lstrip("/"))

    src_out = os.path.join(app, "sourceFiles")
    os.makedirs(src_out)
    for name in sorted(os.listdir(source_dir)):
        path = os.path.join(source_dir, name)
        if os.path.isfile(path) and name.endswith(SOURCE_PATTERNS):
            shutil.copyfile(path, os.path.join(src_out, name))

    unpack_wheels(wheels, os.path.join(app, "lib"))
    shutil.copyfile(os.path.join(HERE, "secretspace.py"), os.path.join(app, "secretspace.py"))
    write(os.path.join(app, "installed"), MARKER_TEXT)

    write(os.path.join(tree, "usr", "bin", "secretspace"), LAUNCHER, 0o755)
    write(os.path.join(tree, "usr", "share", "applications", "secretspace.desktop"),
          DESKTOP_ENTRY)
    icon = os.path.join(tree, "usr", "share", "icons", "hicolor", "512x512",
                        "apps", "secretspace.png")
    os.makedirs(os.path.dirname(icon))
    shutil.copyfile(os.path.join(source_dir, "SecretSpace-logo.png"), icon)
    write(os.path.join(tree, "usr", "share", "doc", PACKAGE, "copyright"),
          copyright_text(pins))

    # Everything readable by all, writable by root only; dpkg-deb records
    # these modes and --root-owner-group makes root the owner.
    for dirpath, dirnames, filenames in os.walk(tree):
        os.chmod(dirpath, 0o755)
        for name in filenames:
            path = os.path.join(dirpath, name)
            os.chmod(path, 0o755 if path.endswith(os.path.join("bin", "secretspace")) else 0o644)

    size = sum(os.path.getsize(os.path.join(d, n))
               for d, _, files in os.walk(tree) for n in files)
    debian = os.path.join(tree, "DEBIAN")
    write(os.path.join(debian, "control"), control(version, math.ceil(size / 1024)))
    write(os.path.join(debian, "postinst"), POSTINST, 0o755)
    write(os.path.join(debian, "prerm"), PRERM, 0o755)
    os.chmod(debian, 0o755)
    return tree


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build the SecretSpace .deb.")
    parser.add_argument("--out", default=os.path.join(ROOT, "build"),
                        help="folder for the .deb (default: build/)")
    args = parser.parse_args(argv)

    if not shutil.which("dpkg-deb"):
        raise SystemExit("dpkg-deb not found: build the package on Debian or Ubuntu")

    version = deb_version(read_version())
    os.makedirs(args.out, exist_ok=True)
    deb = os.path.join(args.out, f"{PACKAGE}_{version}_all.deb")
    with tempfile.TemporaryDirectory(prefix="passman-deb-") as tmp:
        wheels = fetch_wheels(os.path.join(tmp, "wheels"))
        tree = stage(os.path.join(tmp, "tree"), version, wheels, pins=vendored())
        subprocess.run(["dpkg-deb", "--root-owner-group", "-Zxz", "--build", tree, deb],
                       check=True)
    print(deb)
    return 0


if __name__ == "__main__":
    sys.exit(main())
