# PassMan for Linux

The PassMan app for Linux. **Not written yet** — this repository is a
placeholder until it is.

| Repository | What it holds |
|---|---|
| [PassMan-Client-Windows](https://github.com/usermaneGermane/PassMan-Client-Windows) | the app for Windows |
| **PassMan-Client-Linux** (this one) | the app for Linux — not written yet |
| [PassMan-Server-Windows](https://github.com/usermaneGermane/PassMan-Server-Windows) | the sync server for Windows, with an installer |
| [PassMan-Server-Linux](https://github.com/usermaneGermane/PassMan-Server-Linux) | the sync server for Linux, run by systemd |

## The starting point

The Windows app is Python with CustomTkinter, which also runs on Linux, so
the Linux app starts from a copy of PassMan-Client-Windows's `sourceFiles/`.
What has to change is what is Windows-specific there:

- **Where the data lives.** Windows uses `%APPDATA%\PassMan`; Linux should
  use `~/.local/share/passman` (or `$XDG_DATA_HOME/passman`).
- **The clipboard.** `pyperclip` needs `xclip`, `xsel` or `wl-clipboard`
  installed on Linux, and Wayland behaves differently from X11.
- **Packaging.** No Inno Setup: a `.deb` (and later an apt repository), with
  a `.desktop` file for the application menu.
- **Fonts and the look**, which differ per desktop.

Whatever it becomes, it must read and write the same vault files
(`PMV2`, see "Vault format" in PassMan-Client-Windows's README) and speak
the same sync protocol, so that a vault moves between a Windows PC and a
Linux PC unchanged and both can sync with either server.
