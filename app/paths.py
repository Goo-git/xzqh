"""Default-path helpers that survive PyInstaller's frozen layout."""

from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    """Directory the user sees as "the app".

    - Frozen (PyInstaller): folder containing the exe — what users will treat
      as the working dir.
    - Source: the repo root (parent of ``app/``).
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def default_data_dir() -> Path:
    return app_root() / "data"


def default_output_dir() -> Path:
    return app_root() / "dist"


def tools_dir() -> Path:
    """Where the wrapped CLI scripts live.

    When frozen, ``tools/`` is bundled into the package import path via
    PyInstaller; this returns a directory that exists in either layout so it's
    safe to display in UIs.
    """
    src_tools = Path(__file__).resolve().parent.parent / "tools"
    if src_tools.is_dir():
        return src_tools
    return app_root() / "tools"


def icon_path() -> Path | None:
    """Resolve the bundled PNG icon for QIcon use at runtime.

    Looks in PyInstaller's _MEIPASS first (when frozen, where datas are
    extracted), then falls back to the source tree. Returns None if neither
    exists so callers can degrade gracefully.
    """
    candidates: list[Path] = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "assets" / "icon.png")
    candidates.append(Path(__file__).resolve().parent.parent / "assets" / "icon.png")
    for p in candidates:
        if p.is_file():
            return p
    return None
