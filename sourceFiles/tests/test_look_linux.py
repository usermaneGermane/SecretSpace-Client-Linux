"""
Light and dark on Linux: the desktop is asked once.

CustomTkinter's own "system" mode asks again every 30 ms, and on Linux each
question starts a gsettings process. So this app never leaves it in that
mode: theme.apply_appearance asks once and sets light or dark.
"""
import subprocess

import pytest

pytest.importorskip("customtkinter")

import customtkinter as ctk
from customtkinter.windows.widgets.appearance_mode import AppearanceModeTracker

import theme


@pytest.fixture(autouse=True)
def put_back():
    before = ctk.get_appearance_mode()
    yield
    ctk.set_appearance_mode(before)


def test_importing_the_theme_does_not_leave_system_mode():
    assert AppearanceModeTracker.appearance_mode_set_by != "system"


@pytest.mark.parametrize("dark,shown", [(True, "Dark"), (False, "Light")])
def test_system_is_settled_once(monkeypatch, dark, shown):
    asked = []
    monkeypatch.setattr(theme, "desktop_is_dark",
                        lambda: asked.append(1) or dark)
    theme.apply_appearance("system")
    assert ctk.get_appearance_mode() == shown and asked == [1]
    assert AppearanceModeTracker.appearance_mode_set_by != "system"


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_a_chosen_mode_does_not_ask_the_desktop(monkeypatch, mode):
    monkeypatch.setattr(theme, "desktop_is_dark",
                        lambda: pytest.fail("asked the desktop"))
    theme.apply_appearance(mode)
    assert ctk.get_appearance_mode() == mode.capitalize()


def _gsettings(answers):
    """A stand-in for subprocess.run that answers per key."""
    def run(command, **options):
        assert options.get("timeout") == 2
        reply = answers[command[-1]]
        if isinstance(reply, Exception):
            raise reply
        return subprocess.CompletedProcess(command, 0, reply.encode(), b"")
    return run


@pytest.mark.parametrize("answers,dark", [
    ({"color-scheme": "'prefer-dark'\n"}, True),
    ({"color-scheme": "'default'\n"}, False),
    ({"color-scheme": "", "gtk-theme": "'Yaru-dark'\n"}, True),      # older
    ({"color-scheme": "", "gtk-theme": "'Yaru'\n"}, False),
    ({"color-scheme": "", "gtk-theme": ""}, False),                  # no answer
    ({"color-scheme": FileNotFoundError("gsettings")}, False),       # no tool
    ({"color-scheme": subprocess.TimeoutExpired("gsettings", 2)}, False),
])
def test_what_the_desktop_says(monkeypatch, answers, dark):
    monkeypatch.setattr(subprocess, "run", _gsettings(answers))
    assert theme.desktop_is_dark() is dark
