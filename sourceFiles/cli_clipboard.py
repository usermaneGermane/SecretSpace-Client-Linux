"""
The clipboard for the command line, on Linux: Tk's own, as in the app
(clipboard.py). What is copied belongs to this program and is gone when it
ends -- unless a clipboard manager kept its own copy. (SecretSpace for
Windows has its own file of this name.)
"""


class NoClipboard(Exception):
    """There is no clipboard to copy to."""


def hold(text: str, seconds: float) -> None:
    """
    Put ``text`` on the clipboard for ``seconds``, then clear it -- at once
    when interrupted. A text copied by something else meanwhile is left
    alone.
    """
    # Late: every other command works without Tk, also where it is missing.
    try:
        import tkinter as tk
        import clipboard
    except ImportError:
        raise NoClipboard("Tk is not installed (python3-tk).") from None
    try:
        root = tk.Tk()
    except tk.TclError:
        raise NoClipboard("There is no desktop here to copy to. Pipe the "
                          "field into a program instead: get") from None
    try:
        root.withdraw()
        clipboard.copy(root, text)
        root.after(int(seconds * 1000), root.quit)

        def tick():                 # lets Ctrl+C through
            root.after(200, tick)

        tick()
        try:
            root.mainloop()
        except KeyboardInterrupt:
            pass
        if clipboard.paste(root) == text:
            root.clipboard_clear()
            root.update()
    finally:
        root.destroy()
