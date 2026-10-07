"""The Tk clipboard wrapper, against a stand-in root: no display needed."""

import tkinter as tk

import clipboard


class FakeRoot:
    def __init__(self):
        self.content = None
        self.flushed = 0

    def clipboard_clear(self):
        self.content = None

    def clipboard_append(self, text):
        self.content = (self.content or "") + text

    def clipboard_get(self):
        if self.content is None:
            raise tk.TclError("CLIPBOARD selection doesn't exist")
        return self.content

    def update_idletasks(self):
        self.flushed += 1


def test_copy_replaces_what_was_there():
    root = FakeRoot()
    clipboard.copy(root, "old")
    clipboard.copy(root, "secret")
    assert clipboard.paste(root) == "secret"
    assert root.flushed == 2


def test_an_empty_clipboard_reads_as_none():
    assert clipboard.paste(FakeRoot()) is None
