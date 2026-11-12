"""
Single source of truth for the application version.

Read by gui.py for the labels shown in the UI. Bump this on release; keep it
in step with the vault container versions when the on-disk format changes.

A test version carries a pre-release tag, ``1.0.0-alpha.1``; the .deb
spells it 1.0.0~alpha.1 (deb/build_deb.deb_version) so it sorts before
1.0.0. :func:`file_version` is the same as in SecretSpace for Windows, where it
gives the exe four plain numbers.
"""

import re

__version__ = "1.0.0-alpha.8"

#: The container a 3.0 account's vaults are written in (account_crypto).
VAULT_FORMAT = "PMV3"
#: The 2.x container, which 3.0 only reads, to import it (crypto_utils).
LEGACY_VAULT_FORMAT = "PMV2"

_VERSION = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:-(?:alpha|beta|rc)\.(\d+))?")


def file_version(text: str = __version__) -> tuple:
    """(1, 0, 0, 1) for '1.0.0-alpha.1', (1, 0, 0, 0) for '1.0.0'."""
    m = _VERSION.fullmatch(text)
    if not m:
        raise ValueError(f"Not a SecretSpace version: {text!r}")
    return tuple(int(g or 0) for g in m.groups())


def version_string() -> str:
    """e.g. 'v1.0.0' — what the UI shows."""
    return f"v{__version__}"


def long_version_string() -> str:
    """e.g. 'SecretSpace for Linux v1.0.0 · vault format PMV3' — for the
    Settings footer."""
    return f"SecretSpace for Linux {version_string()} · vault format {VAULT_FORMAT}"
