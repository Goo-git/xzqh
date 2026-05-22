"""QThread wrapper around ``tools.fetch_xzqh.run``."""

from __future__ import annotations

import argparse
import threading
import traceback

from PySide6.QtCore import QThread, Signal

from tools import fetch_xzqh


class FetchWorker(QThread):
    log = Signal(str)
    progress = Signal(int, int)   # done, total
    finished_ok = Signal()
    failed = Signal(str)

    def __init__(self, args: argparse.Namespace, parent=None) -> None:
        super().__init__(parent)
        self._args = args
        self._cancel = threading.Event()

    def cancel(self) -> None:
        self._cancel.set()

    def run(self) -> None:  # noqa: D401  (QThread.run convention)
        try:
            fetch_xzqh.run(
                self._args,
                on_log=self.log.emit,
                on_progress=lambda d, t: self.progress.emit(d, t),
                should_cancel=self._cancel.is_set,
            )
        except fetch_xzqh.FetchCancelled:
            self.log.emit("=== 已取消 ===")
            self.failed.emit("已取消")
            return
        except Exception as exc:  # noqa: BLE001  (surface any error to UI)
            self.log.emit("=== 抓取失败 ===")
            self.log.emit(traceback.format_exc())
            self.failed.emit(str(exc))
            return
        self.finished_ok.emit()
