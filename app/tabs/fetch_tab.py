"""Fetch tab: configure & run the MCA scraper."""

from __future__ import annotations

import argparse

from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.paths import default_data_dir
from app.widgets.log_view import LogView
from app.workers.fetch_worker import FetchWorker


class FetchTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._worker: FetchWorker | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        form_box = QGroupBox("参数")
        form = QFormLayout(form_box)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)
        form.setContentsMargins(14, 18, 14, 14)

        self.output_dir = QLineEdit(str(default_data_dir()))
        pick_out = QPushButton("浏览…")
        pick_out.clicked.connect(self._pick_output_dir)
        out_row = QHBoxLayout()
        out_row.addWidget(self.output_dir, stretch=1)
        out_row.addWidget(pick_out)
        form.addRow("输出目录 (--output-dir):", _wrap(out_row))

        self.timeout = QSpinBox()
        self.timeout.setRange(5, 600)
        self.timeout.setValue(60)
        self.timeout.setSuffix(" 秒")
        form.addRow("超时 (--timeout):", self.timeout)

        self.sleep = QDoubleSpinBox()
        self.sleep.setRange(0.0, 10.0)
        self.sleep.setSingleStep(0.1)
        self.sleep.setValue(0.2)
        self.sleep.setSuffix(" 秒")
        form.addRow("省间隔 (--sleep):", self.sleep)

        self.workers = QSpinBox()
        self.workers.setRange(1, 16)
        self.workers.setValue(2)
        form.addRow("县级并发 (--workers):", self.workers)

        self.county_sleep = QDoubleSpinBox()
        self.county_sleep.setRange(0.0, 10.0)
        self.county_sleep.setSingleStep(0.1)
        self.county_sleep.setValue(0.3)
        self.county_sleep.setSuffix(" 秒")
        form.addRow("县级间隔 (--county-sleep):", self.county_sleep)

        self.no_townships = QCheckBox("只抓到县级 (--no-townships)")
        form.addRow(self.no_townships)

        self.reuse = QCheckBox("复用已有 JSON (--reuse)")
        form.addRow(self.reuse)

        root.addWidget(form_box)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        self.start_btn = QPushButton("开始抓取")
        self.start_btn.setProperty("primary", True)
        self.start_btn.clicked.connect(self._start)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setProperty("danger", True)
        self.cancel_btn.clicked.connect(self._cancel)
        self.cancel_btn.setEnabled(False)
        button_row.addStretch(1)
        button_row.addWidget(self.cancel_btn)
        button_row.addWidget(self.start_btn)
        root.addLayout(button_row)

        self.log = LogView()
        root.addWidget(self.log, stretch=1)

    def _pick_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择输出目录", self.output_dir.text())
        if path:
            self.output_dir.setText(path)

    def _collect_args(self) -> argparse.Namespace:
        return argparse.Namespace(
            output_dir=self.output_dir.text() or "data",
            timeout=self.timeout.value(),
            sleep=self.sleep.value(),
            workers=self.workers.value(),
            county_sleep=self.county_sleep.value(),
            no_townships=self.no_townships.isChecked(),
            reuse=self.reuse.isChecked(),
        )

    def _start(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        self.log.clear()
        self.log.set_progress(0, 0)
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)

        self._worker = FetchWorker(self._collect_args(), self)
        self._worker.log.connect(self.log.append)
        self._worker.progress.connect(self.log.set_progress)
        self._worker.finished_ok.connect(self._on_done)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

    def _cancel(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self.cancel_btn.setEnabled(False)
            self.log.append("--- 请求取消，等待当前省份完成 ---")
            self._worker.cancel()

    def _on_done(self) -> None:
        self.log.set_idle("完成")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

    def _on_failed(self, msg: str) -> None:
        self.log.set_idle(f"失败：{msg[:40]}")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)


def _wrap(layout) -> QWidget:
    holder = QWidget()
    holder.setLayout(layout)
    return holder
