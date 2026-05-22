"""Log + progress widget reused by Fetch/Generate tabs."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QPlainTextEdit,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class LogView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.progress = QProgressBar(self)
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("空闲")
        layout.addWidget(self.progress)

        self.text = QPlainTextEdit(self)
        self.text.setReadOnly(True)
        self.text.setMaximumBlockCount(5000)
        self.text.setPlaceholderText("日志输出会显示在这里…")
        mono = QFont("Cascadia Mono")
        mono.setStyleHint(QFont.StyleHint.Monospace)
        mono.setPointSize(10)
        self.text.setFont(mono)
        layout.addWidget(self.text, stretch=1)

    def append(self, line: str) -> None:
        self.text.appendPlainText(line)
        bar = self.text.verticalScrollBar()
        bar.setValue(bar.maximum())

    def clear(self) -> None:
        self.text.clear()

    def set_progress(self, done: int, total: int) -> None:
        if total <= 0:
            self.progress.setRange(0, 0)  # indeterminate
            self.progress.setFormat("处理中…")
            return
        self.progress.setRange(0, total)
        self.progress.setValue(done)
        self.progress.setFormat(f"{done}/{total}")

    def set_idle(self, label: str = "空闲") -> None:
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setFormat(label)
