"""QThread wrapper around ``tools.generate_sql.run``."""

from __future__ import annotations

import argparse
import traceback

from PySide6.QtCore import QThread, Signal

from tools import generate_sql


class GenerateWorker(QThread):
    log = Signal(str)
    finished_ok = Signal()
    failed = Signal(str)

    def __init__(self, args: argparse.Namespace, parent=None) -> None:
        super().__init__(parent)
        self._args = args

    def run(self) -> None:
        try:
            generate_sql.run(self._args, on_log=self.log.emit)
        except Exception as exc:  # noqa: BLE001
            self.log.emit("=== 生成失败 ===")
            self.log.emit(traceback.format_exc())
            self.failed.emit(str(exc))
            return
        self.finished_ok.emit()
