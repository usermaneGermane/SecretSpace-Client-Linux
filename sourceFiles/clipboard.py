"""
The clipboard, through Tk.

On Linux pyperclip needs xclip, xsel or wl-clipboard installed and fails
without them. Tk's own clipboard needs nothing: it works on X11 and, through
XWayland, on Wayland desktops. It also suits a password manager: on X11 the
clipboard belongs to the program that copied, so what SecretSpace copied is gone
once SecretSpace closes -- unless a clipboard manager kept its own copy.
"""

import tkinter as tk


def copy(root, text: str) -> None:
    """Put ``text`` on the clipboard. Raises tk.TclError if it cannot."""
    root.clipboard_clear()
    root.clipboard_append(text)
    # Hand it to the X server now, not at the next idle moment.
    root.update_idletasks()


def paste(root):
    """What the clipboard holds as text, or None if empty or not text."""
    try:
        return root.clipboard_get()
    except tk.TclError:
        return None
