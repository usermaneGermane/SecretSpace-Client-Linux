# SecretSpace for Linux

A local desktop password manager. Your vault is a single AES-256-GCM
encrypted file. There is no online account and no service behind it: it works
entirely offline, and if you want two PCs in step you run the sync server
yourself, on your own hardware.

**Formerly PassMan.** The project was renamed to SecretSpace in November
2026, because another password manager already uses the name PassMan.
Releases up to 0.9.0 are the `passman` package (command
`passman`, data in `~/.local/share/passman`). Installing the `secretspace`
package replaces it in one step (`Conflicts`/`Replaces: passman`), and your
vaults stay in `~/.local/share/passman`, which SecretSpace keeps using —
nothing is moved or renamed. The vault files are the same.

**Version 0.11.0 — early.** It installs from a `.deb` on Ubuntu 22.04 or
newer, or runs from source. It has so far been tested in CI only, on a
virtual display, not yet on a real desktop.

![SecretSpace](sourceFiles/SecretSpace-logo.png)

| Repository | What it holds |
|---|---|
| [SecretSpace-Client-Windows](https://github.com/usermaneGermane/SecretSpace-Client-Windows) | the app for Windows |
| **SecretSpace-Client-Linux** (this one) | the app for Linux |
| [SecretSpace-Server-Windows](https://github.com/usermaneGermane/SecretSpace-Server-Windows) | the sync server for Windows, with an installer |
| [SecretSpace-Server-Linux](https://github.com/usermaneGermane/SecretSpace-Server-Linux) | the sync server for Linux, run by systemd |

**Same vaults as on Windows.** The vault file, the sync protocol and the
features match SecretSpace for Windows 2.11.0, including its black-and-green
window and dialogs, 2FA codes and sync on unlock (see the version table under *What is different from
Windows*).
A vault moves between a Windows PC and a Linux PC unchanged, and both sync
with either server.

## Installing it

The package is `secretspace_<version>_all.deb`. Download it from
[Releases](https://github.com/usermaneGermane/SecretSpace-Client-Linux/releases)
(checksums in `SHA256SUMS.txt`), take the newest build from the
`secretspace-deb` artifact of the latest CI run on `main`
(`gh run download -R usermaneGermane/SecretSpace-Client-Linux -n secretspace-deb`),
or build it yourself on Ubuntu or Debian:

```bash
sudo apt install git python3-pip
git clone https://github.com/usermaneGermane/SecretSpace-Client-Linux.git
cd SecretSpace-Client-Linux
python3 deb/build_deb.py          # writes build/secretspace_<version>_all.deb
```

Then install it — apt pulls in Tk, cryptography, Argon2 (`python3-argon2`, in
the *universe* section, on by default on Ubuntu desktops) and Pillow from Ubuntu:

```bash
sudo apt install ./build/secretspace_*_all.deb
```

SecretSpace is then in the application menu, and `secretspace` starts it from a
terminal. `sudo apt remove secretspace` removes the program and leaves your
vaults alone.

| Installed file | What it is |
| --- | --- |
| `/usr/bin/secretspace` | starts the app |
| `/usr/lib/secretspace/` | the program and the libraries it bundles (customtkinter, darkdetect, packaging — pinned by hash in `deb/vendor.txt`) |
| `/usr/share/applications/secretspace.desktop` | the menu entry |

## Running from source

On Ubuntu 22.04 or newer (other desktops with Python 3.10+ and Tk work the
same way):

```bash
sudo apt install python3-tk python3-venv git
git clone https://github.com/usermaneGermane/SecretSpace-Client-Linux.git ~/SecretSpace-Client-Linux
cd ~/SecretSpace-Client-Linux
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python sourceFiles/gui.py
```

After that, starting it is the last line, from that folder.

## Where your data lives

Run from a checkout, as above, the files are in the checkout itself, next
to `sourceFiles/` — the same rule as a portable copy on Windows. The
package keeps them in **`~/.local/share/secretspace`**
(or `$XDG_DATA_HOME/secretspace`) instead, so that upgrading or removing it never
touches them — or in `~/.local/share/passman`, if that folder was there
first, from the `passman` package before the rename. `PASSMAN_DATA_DIR` points the app at any other vault folder.

**Lab and production.** The package is the production copy. A checkout is a
handy lab copy beside it: it never touches `~/.local/share/secretspace`, and its
window title says `[LAB - <its vault folder>]` (the package's never does).
If both sync to the same server, give lab vaults names your real vaults do
not use — the server keeps one vault per username, so a lab vault with a
real vault's name would sync into it.

| File | What it is |
| --- | --- |
| `vault/<user>.vault.enc` | your encrypted vault |
| `vault/<user>.vault.enc.bak` | the previous version, kept automatically |
| `vault/<user>.vault.enc.base` | what the server held at the last sync, and which server that was; only if you sync |
| `config.json` | non-secret preferences (last username, auto-lock delay, sort order) |

The vault files are readable by your user only (`600`), and so is the
`vault` folder (`700`) when SecretSpace creates it. A plaintext CSV export is
created `600` too — it holds every password in the clear, so delete it once
it has done its job.

**Moving a vault from Windows:** copy `%APPDATA%\SecretSpace\vault\<user>.vault.enc`
into the `vault` folder here, or use *Restore from server* on the login
screen if you sync.

## What is different from Windows

- **Clipboard.** SecretSpace uses Tk's own clipboard, so nothing like `xclip`
  needs installing. It works on X11 and, through XWayland, on Wayland. On
  X11 what SecretSpace copied disappears when SecretSpace closes. As on Windows,
  locking leaves a copied password pasteable, closing clears it at once, and
  copied passwords are cleared after 30 seconds — but a clipboard manager
  (GNOME or KDE clipboard history, CopyQ, …) may keep its own copy, which
  no application can reach.
- **Fonts.** DejaVu Sans, which Ubuntu ships; elsewhere fontconfig picks the
  nearest.
- **A package instead of an installer.** The `.deb` does what the Windows
  installer does: a menu entry, data in your home folder, removal that keeps
  the vaults. Unlike the Windows installer it does not offer to move a vault
  from a copy run from source — copy the `vault` folder into
  `~/.local/share/secretspace` yourself.

Everything else — syncing (and sync on unlock), the archive, revision history, 2FA codes,
importing from other password managers, and the security notes and limits — works and
reads exactly as in [SecretSpace for Windows's
README](https://github.com/usermaneGermane/SecretSpace-Client-Windows#syncing-two-pcs).
Where that README names a Windows version, read the Linux one beside it:

| Windows | Linux | What arrived |
|---|---|---|
| 2.3.0 | 0.1.0 | the Linux app |
| 2.4.0 | 0.3.0 | deleting archived entries after N days |
| 2.5.0 | 0.4.0 | switching servers no longer removes entries silently |
| 2.6.0 | 0.5.0 | a copy that is not installed says LAB in its title |
| 2.7.0 | 0.7.0 | the redesigned window |
| 2.8.0 | 0.6.0 | locking no longer clears a copied password |
| 2.9.0 | 0.7.0 | the dialogs redesigned to match |
| 2.10.0 | 0.8.0 | 2FA codes, behind the master password |
| 2.11.0 | 0.9.0 | sync on unlock, a setting that is off by default |
| 2.12.0 | 0.10.0 | renamed to SecretSpace (package `secretspace`, replaces `passman`) |
| 2.13.0 | 0.11.0 | a smoother look: smoothed corners, redrawn sign-in backdrop |

(0.2.0 added the `.deb` package, which has no Windows counterpart.)

## Important: your master password cannot be recovered

The master password *is* the encryption key. Nobody can decrypt your vault
without it, and there is no reset and no recovery. **Make backups:**
Settings → *Encrypted backup* → *Save backup…* writes a copy that is still protected by
your master password.

## Project layout

```
SecretSpace-Client-Linux/
├── sourceFiles/        the program — ported from SecretSpace-Client-Windows
│   ├── gui.py          app shell: login, account list, lifecycle
│   ├── clipboard.py    the clipboard, through Tk (Linux only)
│   ├── ...             the same modules as on Windows
│   └── tests/
│       └── sync_server/ a copy of the server, for the end-to-end sync tests
├── deb/
│   ├── build_deb.py    builds the .deb
│   ├── secretspace.py      the launcher installed in /usr/lib/secretspace
│   └── vendor.txt      the libraries bundled into the package, pinned by hash
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

The `deb` job, on Ubuntu 22.04 and 24.04, builds the package, installs it
with apt, runs the tests on the system's own Python, Tk, cryptography and
Pillow, runs the smoke test against the installed copy
(`tools/smoke_gui.py --installed`), starts `secretspace` as the menu would, and
removes the package again. The 24.04 run keeps the `.deb` as the
`secretspace-deb` artifact.

**Staying in step with Windows.** The modules here began as copies of
SecretSpace-Client-Windows's `sourceFiles/`; only `vault.py` (where data lives,
file modes), `gui.py` (clipboard, window icon), `theme.py` (fonts),
`version.py`, `password_generator.py` and the new `clipboard.py` differ. A
fix to the shared logic — the vault, sync, importers — belongs in both
repositories.

## License

SecretSpace for Linux is free software under the **GNU General Public License
v3.0 only** (GPL-3.0-only) — see [LICENSE](LICENSE). You may use, study,
change and share it; if you distribute a changed version, it must stay under
the same licence, with its source.

The other SecretSpace repositories (the Windows and Linux clients and sync servers)
are free software under the same licence.

Security issues: please report them privately, see [SECURITY.md](SECURITY.md).
