# SecretSpace for Linux

A desktop password manager that you run entirely yourself. Your passwords
are in encrypted vaults on your own PC (AES-256-GCM; the key comes from your
master password and a Secret Key, through Argon2id). There is no online
service behind it: it works offline, and if you want several devices in
step, or a vault shared with other people, you run the sync server yourself,
on your own hardware.

**Formerly PassMan.** The project was renamed to SecretSpace in November
2026, because another password manager already uses the name PassMan. The
names you see changed then; SecretSpace 3 (Linux 1.x) still carried the old
name where nobody looks — in the labels its keys are made with, in the
markers at the start of its files, in the name of its data folder. **Since
2.0.0 nothing the app makes carries the old name.** That is why 2.0.0 has a
new file format and converts an account from 1.x; the cryptography itself
is unchanged. (Releases up to 0.9.0 were the `passman` package; installing
`secretspace` replaces it in one step.)

**This README describes SecretSpace 4 for Linux** (2.0.0), the same
release as SecretSpace for Windows 4.0.0. Coming from 1.x? Read
[Upgrading from 1.x](#upgrading-from-1x) first: your account is converted
the first time you unlock it. Coming from 0.x? Read
[Upgrading from 0.x](#upgrading-from-0x). The 0.x line — one vault file per
user, last release
[0.11.0](https://github.com/usermaneGermane/SecretSpace-Client-Linux/releases/tag/v0.11.0) —
is finished; its README is on the branch
[`release-0.x`](https://github.com/usermaneGermane/SecretSpace-Client-Linux/tree/release-0.x).

It installs from a `.deb` on Ubuntu 22.04 or newer, or runs from source. It
has so far been tested in CI only (Ubuntu 22.04 and 24.04, on a virtual
display), not yet on a real desktop.

![SecretSpace](sourceFiles/SecretSpace-logo.png)

| Repository | What it holds |
|---|---|
| [SecretSpace-Client-Windows](https://github.com/usermaneGermane/SecretSpace-Client-Windows) | the app for Windows |
| **SecretSpace-Client-Linux** (this one) | the app for Linux |
| [SecretSpace-Server-Windows](https://github.com/usermaneGermane/SecretSpace-Server-Windows) | the sync server for Windows, with an installer |
| [SecretSpace-Server-Linux](https://github.com/usermaneGermane/SecretSpace-Server-Linux) | the sync server for Linux, run by systemd |

**The same as on Windows.** The account and vault files, the sync protocol
and the features match SecretSpace for Windows (see the version table under
*What is different from Windows*): 1.0.0 = Windows 3.0.0, 1.1.0 =
Windows 3.1.0, 2.0.0 = Windows 4.0.0. An account moves
between a Windows PC and a Linux PC through the server, and both sync with
either server.

## What SecretSpace is

1.0.0 is the same release as [SecretSpace for Windows
3.0.0](https://github.com/usermaneGermane/SecretSpace-Client-Windows#what-secretspace-3-is), whose README
describes each part in full:

- **Accounts** instead of one vault file per user, with a **Secret Key**
  (in your Emergency Kit) and a **12-word recovery phrase**; the key comes
  from the master password and the Secret Key through Argon2id.
- **Several vaults** in one account (*Vaults* above the list), each with its
  own key.
- **Sync** through your own SecretSpace Server **2.1.0** or newer
  (*Settings → Sync → Set up…*; on another device *Sign in from a server*).
  The account and its vaults are files on this PC, so they open with no
  network at all.
- **Sharing a vault** with other accounts of the same server (*Vaults →
  Members*: owner, editor or reader, a fingerprint check before the first
  share, and *Remove* gives the vault a new key). Vault keys are signed, so
  a dishonest server cannot slip in a key of its own.
- **Who changed what** (*Vaults → Activity*), a signed record in every
  vault — never of who viewed or copied a password.
- **Recovery:** *Forgot your master password?* on the login screen opens the
  account with the 12-word phrase, sets a new password and makes a new
  phrase.
- **Importing 0.x / 2.x vaults** with their history and archive.

Not in 1.0: a company setup (admin console, invites), adding someone before
they have an account, moving an entry between vaults, and *Sync when I
unlock* (0.x has it; here you press **Sync**).

On Linux:

- **The Secret Key is kept under your master password** (Argon2id, then
  AES-GCM), not by the system as Windows does with DPAPI. So a copy of the
  account folder opens on another PC with the master password alone; keep
  your backups as private as your vault files. The desktop keyring may take
  this over later. It also means that **after a recovery the account gets a
  new Secret Key** (the stored one is sealed under the forgotten password):
  save the new Emergency Kit the recovery shows you.
- The account folders are `700` and their files `600`, like the vault
  folder; a saved Emergency Kit is `600` too.
- *Settings → Backup → Open folder* opens the folder with `xdg-open`.

| File | What it is |
| --- | --- |
| `accounts/<name>/account.json` | nothing secret, and the Secret Key sealed under your master password |
| `accounts/<name>/keyset.ssk` | the account's keys, under master password + Secret Key |
| `accounts/<name>/recovery.ssk` | the same keys, under the 12-word recovery phrase |
| `accounts/<name>/vaults/<id>.ssv` | one vault's entries (+ `.bak`) |

They sit beside the `vault` folder described under *Where your data lives*,
which holds 0.x vaults and is only read, for *Import*.

## New in 1.1: the look

- **Light and dark.** The app follows the desktop; *Settings → Appearance*
  chooses one.
- **A typeface of its own**, Manrope, and line icons the app draws itself.
- **The main window has three columns:** your vaults down the left (with
  how many entries each has, and "shared" where other people are in it),
  the entries, and the selected entry. *Sync* and *Lock* sit with your
  account at the bottom left.
- Entries, vaults and members are cards of their own, with pastel tiles.
- Nothing changes in what the app does or stores: it opens the same
  accounts, and going back to 1.0.0 is just installing that package again
  (`sudo apt install --allow-downgrades ./secretspace_1.0.0_all.deb`).

1.1.0 is the same release as SecretSpace for Windows 3.1.0.

## Upgrading from 1.x

2.0.0 writes accounts in a new format and **converts an account from 1.x
the first time you unlock it**. Your entries, vaults, master password and
12 recovery words stay the same. What you need to know first:

- **SecretSpace 1.x (and Windows 3.x) cannot open a converted account.**
  Update SecretSpace on **every device** that uses the account before you
  sync them again; a device still on the old version is refused by the
  server afterwards (its message speaks of a changed master password — it
  means "update me").
- **The sync server must be 2.1.0 or newer.** Update it first; it keeps
  serving older apps. Until then 2.0.0 works on your PC and says the server
  is too old when you press Sync.
- **Your Emergency Kit stays valid.** A Secret Key printed by 1.x starts
  with `A3-`; 2.0.0 accepts it and shows the same key as `A4-…`.
- **Fingerprint digits change.** The digits two people compare before
  sharing a vault are new in this version. Nothing you already compared
  has to be compared again, but compare with someone only once you have
  both updated: an older app shows other digits for the same account.

The steps:

1. **Back up first.** Close SecretSpace and copy `~/.local/share/secretspace`
   (or `~/.local/share/passman`, if that is the one you have).
2. **Update the server** to 2.1.0, if you sync.
3. **Install 2.0.0** (below). At its first start the app renames the data
   folder `~/.local/share/passman` to `~/.local/share/secretspace`, if
   yours still had the old name (renamed, not copied).
4. **Unlock.** After your master password, SecretSpace says the account
   will be converted. *Save a copy first…* puts a copy of the account as it
   is in a folder you choose; *Convert* does it. It needs no network.
5. **Type your 12 recovery words once**, when asked. The recovery copy opens
   only with those words, so only you can have it converted; the words stay
   the same. You can do it later (Settings → Security → *Recovery copy*).
6. **Sync.** The server is told about the conversion, and your vaults are
   stored in the new format. A vault you **share** moves to the new format
   by itself once every member has updated and unlocked once; until then it
   stays readable for a member on the older version.

**Going back.** Install 1.1.0 again
(`sudo apt install --allow-downgrades ./secretspace_1.1.0_all.deb`) and put
back the copy of the account you saved in step 4, or the backup from step 1.

The formats, and how a conversion keeps an account's keys and signatures
valid, are described in the Windows app's README under
[The account files](https://github.com/usermaneGermane/SecretSpace-Client-Windows#the-account-files);
they are the same here.

## Upgrading from 0.x

SecretSpace 3 does not open 0.x vaults directly: you make an account and
**import** them. **Your 0.x vaults are never converted, changed or
deleted**, so the way back stays open.

1. **Back up first.** Close SecretSpace and copy `~/.local/share/secretspace`
   (or `~/.local/share/passman`, if that is the one you have).
2. **Install the latest release** (below). It replaces the 0.x package; the data folder
   is left as it is.
3. **Create an account.** The login screen is empty at first — your 0.x
   vaults are not shown there. Save the Emergency Kit and write down the
   12-word phrase.
4. **Import.** Press *Import*, pick a vault from the list and enter its
   master password. Its entries arrive whole, with history and archive, in
   the vault that is shown.
5. **Sync.** The old sync settings are not carried over. Update your server
   to **2.1.0** (it keeps serving 0.x and 2.x apps exactly as before), then
   use *Settings → Sync → Set up…*.

**Going back.** Install the
[0.11.0](https://github.com/usermaneGermane/SecretSpace-Client-Linux/releases/tag/v0.11.0)
package again (`sudo apt install --allow-downgrades ./secretspace_0.11.0_all.deb`).
It opens your 0.x vaults as you left them. What you added in SecretSpace 3
stays in the account: there is no sync between a 0.x vault and an account.

## Installing it

The package is `secretspace_<version>_all.deb`. Download it from
[Releases](https://github.com/usermaneGermane/SecretSpace-Client-Linux/releases)
(the release marked **Latest**; checksums in `SHA256SUMS.txt`; a
*Pre-release* is a test version), or build it yourself on Ubuntu or Debian.
CI also keeps a `secretspace-deb` artifact of each run on `main`; that one may
be ahead of the release and is for testing only.

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
touches them. (A folder `~/.local/share/passman` from before the rename is
renamed to that at the app's first start.) `SECRETSPACE_DATA_DIR` points the app at any other vault folder.

**Lab and production.** The package is the production copy. A checkout is a
handy lab copy beside it: it never touches `~/.local/share/secretspace`, and its
window title says `[LAB - <its vault folder>]` (the package's never does).
If both sync to the same server, give lab accounts names your real accounts
do not use — the server has one account per name.

Your account is in the `accounts` folder there (see the table under *What
SecretSpace 3 is*). The `vault` folder beside it holds 0.x vaults, if you
had any:

| File | What it is |
| --- | --- |
| `vault/<user>.vault.enc` | a 0.x vault; SecretSpace 3 only reads it, for *Import* |
| `vault/<user>.vault.enc.bak` | its previous version |
| `vault/<user>.vault.enc.base` | its sync state with a 1.x server |
| `config.json` | non-secret preferences (last username, auto-lock delay, sort order) |

The vault files are readable by your user only (`600`), and so is the
`vault` folder (`700`) when SecretSpace creates it. A plaintext CSV export is
created `600` too — it holds every password in the clear, so delete it once
it has done its job.

**Moving an account from Windows:** put it on a server there (*Settings →
Sync → Set up…*) and use *Sign in from a server* on the login screen here,
with the Secret Key from your Emergency Kit.

## What is different from Windows

- **Clipboard.** SecretSpace uses Tk's own clipboard, so nothing like `xclip`
  needs installing. It works on X11 and, through XWayland, on Wayland. On
  X11 what SecretSpace copied disappears when SecretSpace closes. As on Windows,
  locking leaves a copied password pasteable, closing clears it at once, and
  copied passwords are cleared after 30 seconds — but a clipboard manager
  (GNOME or KDE clipboard history, CopyQ, …) may keep its own copy, which
  no application can reach.
- **Fonts.** From 1.1 the app brings its own typeface, Manrope (SIL Open
  Font License); it is copied to `~/.fonts` at the first start, which is
  how the toolkit makes a font known. Codes and fingerprints use DejaVu
  Sans Mono, which Ubuntu ships.
- **Light and dark** *(1.1)* follow the desktop where it reports one
  (GNOME's colour scheme, or a theme whose name ends in `-dark`), asked
  **once, at start**: change the desktop while SecretSpace runs and it
  follows at the next start. *Settings → Appearance* chooses one either
  way.
- **A package instead of an installer.** The `.deb` does what the Windows
  installer does: a menu entry, data in your home folder, removal that keeps
  the vaults. Unlike the Windows installer it does not offer to move a vault
  from a copy run from source — copy the `vault` folder into
  `~/.local/share/secretspace` yourself.

Everything else — syncing, the archive, revision history, 2FA codes,
importing from other password managers, and the security notes and limits — works and
reads exactly as in [SecretSpace for Windows's
README](https://github.com/usermaneGermane/SecretSpace-Client-Windows#syncing-your-devices).
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
| 2.13.0 | 0.11.0 | a smoother look, for the stable line (same as alpha.4 below) |
| 3.0.0-alpha.1 | 1.0.0-alpha.1 | PassMan 3 test: accounts, Emergency Kit, recovery phrase, 2.x import |
| 3.0.0-alpha.2 | 1.0.0-alpha.2 | renamed to SecretSpace (package `secretspace`, replaces `passman`) |
| 3.0.0-alpha.3 | 1.0.0-alpha.3 | accounts sync through SecretSpace Server 2.0; sign in from a server |
| 3.0.0-alpha.4 | 1.0.0-alpha.4 | a smoother look: smoothed corners, redrawn sign-in backdrop |
| 3.0.0-alpha.5 | 1.0.0-alpha.5 | several vaults per account; Sync covers them all (Server 2.0.0-alpha.2) |
| 3.0.0-alpha.6 | 1.0.0-alpha.6 | sharing a vault (owner / editor / reader), who changed what (Server 2.0.0-alpha.3) |
| 3.0.0-alpha.7 | 1.0.0-alpha.7 | recovering an account with the 12-word phrase, a new phrase (Server 2.0.0-alpha.4) |
| 3.0.0-alpha.8 | 1.0.0-alpha.8 | security fix: signed vault keys (Server 2.0.0-alpha.5) |
| 3.0.0 | 1.0.0 | SecretSpace 3, the first release: everything from the alpha rows (Server 2.0.0) |
| 3.1.0-alpha.1, alpha.2 | 1.1.0-alpha.2 | the new look: light and dark, the Manrope typeface, vaults down the left of the main window |
| — | 1.1.0-alpha.3 | Linux only: the desktop is asked for light or dark once, not every 30 ms |
| 3.1.0-alpha.3 | 1.1.0-alpha.4 | icons drawn by the app, vault tiles in the Vaults window, no outlined cards |
| 3.1.0 | 1.1.0 | the new look, released: everything from the 3.1 / 1.1 alpha rows |
| 4.0.0 | 2.0.0 | nothing carries the project's old name any more: a new file format, accounts from 1.x are converted (Server 2.1.0) |

(0.2.0 added the `.deb` package, which has no Windows counterpart.)

## If you forget your master password

Nobody can open your account for you, and there is no backdoor. What opens
it without the master password is the **12-word recovery phrase** you wrote
down when you made the account: *Forgot your master password?* on the login
screen. Lose the master password **and** the phrase, and the passwords are
gone. **Make backups:** *Settings → Backup → Open folder* shows the
account's folder; copy it to another drive.

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

The 12-word recovery phrase uses the BIP39 English word list from
[bitcoin/bips](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt).

Security issues: please report them privately, see [SECURITY.md](SECURITY.md).
