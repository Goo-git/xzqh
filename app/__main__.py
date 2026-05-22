"""Entry point: ``python -m app``."""

from __future__ import annotations

import sys
from pathlib import Path

# Make tools/ importable when running from source.
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from PySide6.QtGui import QFont, QIcon  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402  (sys.path tweak first)

from app.main_window import MainWindow  # noqa: E402
from app.paths import icon_path  # noqa: E402
from app.styles import DARK_QSS  # noqa: E402


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("xzqh GUI")
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(DARK_QSS)
    icon_file = icon_path()
    if icon_file is not None:
        app.setWindowIcon(QIcon(str(icon_file)))
    win = MainWindow()
    if icon_file is not None:
        win.setWindowIcon(QIcon(str(icon_file)))
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
