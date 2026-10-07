# PassMan for Linux

A local desktop password manager. Your vault is a single AES-256-GCM
encrypted file. There is no account and no service behind it: it works
entirely offline, and if you want two PCs in step you run the sync server
yourself, on your own hardware.

**Version 0.1.0 — early.** It runs from source on Ubuntu. There is no
package yet; a `.deb` is next.

![PassMan](sourceFiles/PassMan-logo.png)

| Repository | What it holds |
|---|---|
| [PassMan-Client-Windows](https://github.com/usermaneGermane/PassMan-Client-Windows) | the app for Windows |
| **PassMan-Client-Linux** (this one) | the app for Linux |
| [PassMan-Server-Windows](https://github.com/usermaneGermane/PassMan-Server-Windows) | the sync server for Windows, with an installer |
| [PassMan-Server-Linux](https://github.com/usermaneGermane/PassMan-Server-Linux) | the sync server for Linux, run by systemd |

**Same vaults as on Windows.** The vault file, the sync protocol and the
features are those of PassMan for Windows 2.3.0, which this was ported from.
A vault moves between a Windows PC and a Linux PC unchanged, and both sync
with either server.

## Running it

On Ubuntu 22.04 or newer (other desktops with Python 3.10+ and Tk work the
same way):

```bash
sudo apt install python3-tk python3-venv git
git clone https://github.com/usermaneGermane/PassMan-Client-Linux.git ~/PassMan-Client-Linux
cd ~/PassMan-Client-Linux
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python sourceFiles/gui.py
```

After that, starting it is the last line, from that folder.

## Where your data lives

Run from a checkout, as above, the files are in the checkout itself, next
to `sourceFiles/` — the same rule as a portable copy on Windows. The
package, when there is one, will keep them in **`~/.local/share/passman`**
(or `$XDG_DATA_HOME/passman`) instead, so that upgrading or removing it never
touches them. `PASSMAN_DATA_DIR` points the app at any other vault folder.

| File | What it is |
| --- | --- |
| `vault/<user>.vault.enc` | your encrypted vault |
| `vault/<user>.vault.enc.bak` | the previous version, kept automatically |
| `vault/<user>.vault.enc.base` | what the server held at the last sync; only if you sync |
| `config.json` | non-secret preferences (last username, auto-lock delay, sort order) |

The vault files are readable by your user only (`600`), and so is the
`vault` folder (`700`) when PassMan creates it. A plaintext CSV export is
created `600` too — it holds every password in the clear, so delete it once
it has done its job.

**Moving a vault from Windows:** copy `%APPDATA%\PassMan\vault\<user>.vault.enc`
into the `vault` folder here, or use *Restore from server* on the login
screen if you sync.

## What is different from Windows

- **Clipboard.** PassMan uses Tk's own clipboard, so nothing like `xclip`
  needs installing. It works on X11 and, through XWayland, on Wayland. On
  X11 what PassMan copied disappears when PassMan closes. As on Windows,
  copied passwords are cleared after 30 seconds — but a clipboard manager
  (GNOME or KDE clipboard history, CopyQ, …) may keep its own copy, which
  no application can reach.
- **Fonts.** DejaVu Sans, which Ubuntu ships; elsewhere fontconfig picks the
  nearest.
- **No installer yet**, so no application-menu entry and no
  `~/.local/share/passman` until the package exists.

Everything else — syncing, the archive, revision history, importing from
other password managers, and the security notes and limits — works and
reads exactly as in [PassMan for Windows's
README](https://github.com/usermaneGermane/PassMan-Client-Windows#syncing-two-pcs).

## Important: your master password cannot be recovered

The master password *is* the encryption key. Nobody can decrypt your vault
without it, and there is no reset and no recovery. **Make backups:**
Settings → *Save encrypted backup* writes a copy that is still protected by
your master password.

## Project layout

```
PassMan-Client-Linux/
├── sourceFiles/        the program — ported from PassMan-Client-Windows
│   ├── gui.py          app shell: login, account list, lifecycle
│   ├── clipboard.py    the clipboard, through Tk (Linux only)
│   ├── ...             the same modules as on Windows
│   └── tests/
│       └── sync_server/ a copy of the server, for the end-to-end sync tests
└── tools/smoke_gui.py  starts the real app on a display and takes screenshots
```

## Versioning

The version lives in `sourceFiles/version.py` and each release is tagged
`v<version>`. It is separate from the Windows app's: 0.x until the Linux
app is packaged and has been used for real.

## Development

```
pip install -r requirements-dev.txt
python -m pytest -q
```

GitHub Actions runs the tests on Ubuntu with Python 3.10, 3.12 and 3.13, and
`tools/smoke_gui.py` under a virtual display, which starts the app, unlocks
a throwaway vault, copies and clears a password, and keeps screenshots of
the login and main windows as the run's artifact.

**Staying in step with Windows.** The modules here began as copies of
PassMan-Client-Windows's `sourceFiles/`; only `vault.py` (where data lives,
file modes), `gui.py` (clipboard, window icon), `theme.py` (fonts),
`version.py`, `password_generator.py` and the new `clipboard.py` differ. A
fix to the shared logic — the vault, sync, importers — belongs in both
repositories.
