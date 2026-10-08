"""The .deb layout, built from a fake wheel so no network or dpkg is needed.
CI builds and installs the real package in the `deb` job."""

import os
import sys
import zipfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "sourceFiles"))

import build_deb  # noqa: E402
import version  # noqa: E402


@pytest.fixture
def wheel(tmp_path):
    path = tmp_path / "fakelib-1.0-py3-none-any.whl"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("fakelib/__init__.py", "X = 1\n")
        z.writestr("fakelib-1.0.dist-info/LICENSE", "fake\n")
    return str(path)


@pytest.fixture
def tree(tmp_path, wheel):
    return build_deb.stage(str(tmp_path / "tree"), "9.8.7", [wheel],
                           pins=[("fakelib", "1.0")])


def read(tree, *parts):
    with open(os.path.join(tree, *parts), encoding="utf-8") as f:
        return f.read()


def test_version_comes_from_version_py():
    assert build_deb.read_version() == version.__version__


def test_vendored_pins_are_exact():
    pins = dict(build_deb.vendored())
    assert set(pins) == {"customtkinter", "darkdetect", "packaging"}
    assert all(v and v[0].isdigit() for v in pins.values())


def test_program_without_its_tests(tree):
    src = os.path.join(tree, "usr", "lib", "passman", "sourceFiles")
    names = set(os.listdir(src))
    assert {"gui.py", "vault.py", "version.py", "PassMan-logo.png"} <= names
    assert "tests" not in names and "__pycache__" not in names


def test_installed_marker_moves_data_to_home(tree):
    # vault.is_installed() looks for this file next to sourceFiles/.
    assert os.path.isfile(os.path.join(tree, "usr", "lib", "passman", "installed"))


def test_wheels_unpacked_into_lib(tree):
    lib = os.path.join(tree, "usr", "lib", "passman", "lib")
    assert os.path.isfile(os.path.join(lib, "fakelib", "__init__.py"))
    assert os.path.isfile(os.path.join(lib, "fakelib-1.0.dist-info", "LICENSE"))


def test_launcher_runs_isolated_python(tree):
    text = read(tree, "usr", "bin", "passman")
    assert text.startswith("#!/bin/sh\n")
    assert 'exec /usr/bin/python3 -I /usr/lib/passman/passman.py "$@"' in text
    assert os.path.isfile(os.path.join(tree, "usr", "lib", "passman", "passman.py"))


def test_desktop_entry_and_icon(tree):
    entry = read(tree, "usr", "share", "applications", "passman.desktop")
    assert "Exec=passman\n" in entry and "Icon=passman\n" in entry
    assert "StartupWMClass=passman\n" in entry
    assert os.path.isfile(os.path.join(tree, "usr", "share", "icons", "hicolor",
                                        "512x512", "apps", "passman.png"))


def test_control_file(tree):
    text = read(tree, "DEBIAN", "control")
    fields = dict(line.split(": ", 1) for line in text.splitlines()
                  if line and not line.startswith(" "))
    assert fields["Package"] == "passman"
    assert fields["Version"] == "9.8.7"
    assert fields["Architecture"] == "all"
    assert int(fields["Installed-Size"]) > 0
    for dep in ("python3-tk", "python3-cryptography", "python3-pil.imagetk"):
        assert dep in fields["Depends"]
    assert text.endswith("\n")


def test_maintainer_scripts_compile_and_clean(tree):
    assert "py3compile -p passman /usr/lib/passman" in read(tree, "DEBIAN", "postinst")
    assert "py3clean -p passman" in read(tree, "DEBIAN", "prerm")


def test_copyright_lists_bundled_libraries(tree):
    assert "fakelib 1.0" in read(tree, "usr", "share", "doc", "passman", "copyright")


def test_generated_files_use_lf(tree):
    for parts in (("usr", "bin", "passman"), ("DEBIAN", "control"), ("DEBIAN", "prerm")):
        with open(os.path.join(tree, *parts), "rb") as f:
            assert b"\r" not in f.read()


@pytest.mark.skipif(os.name == "nt", reason="POSIX file modes")
def test_file_modes(tree):
    def mode(*parts):
        return os.stat(os.path.join(tree, *parts)).st_mode & 0o777

    assert mode("usr", "bin", "passman") == 0o755
    assert mode("DEBIAN", "postinst") == 0o755
    assert mode("usr", "lib", "passman", "sourceFiles", "gui.py") == 0o644
    assert mode("usr", "lib", "passman") == 0o755


def test_refuses_compiled_wheels(tmp_path, monkeypatch):
    dest = tmp_path / "wheels"
    dest.mkdir()
    (dest / "native-1.0-cp312-cp312-linux_x86_64.whl").write_bytes(b"")
    monkeypatch.setattr(build_deb.subprocess, "run", lambda *a, **k: None)
    with pytest.raises(SystemExit, match="not a pure-Python wheel"):
        build_deb.fetch_wheels(str(dest))
