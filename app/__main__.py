"""Entry point: ``python -m app``."""

from __future__ import annotations

import sys
from pathlib import Path

# Make tools/ importable when running from source.
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from PySide6.QtWidgets import QApplication  # noqa: E402  (sys.path tweak first)

from app.main_window import MainWindow  # noqa: E402


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("xzqh GUI")
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
