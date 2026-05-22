"""Generate tab: produce SQL/CSV from an existing data version."""

from __future__ import annotations

import argparse
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
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

from app.paths import default_data_dir, default_output_dir
from app.widgets.log_view import LogView
from app.workers.generate_worker import GenerateWorker


class GenerateTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._worker: GenerateWorker | None = None
        self._last_out_dir: Path | None = None
        self._build_ui()
        self._reload_versions()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        form_box = QGroupBox("参数")
        form = QFormLayout(form_box)

        self.data_dir = QLineEdit(str(default_data_dir()))
        pick_data = QPushButton("浏览…")
        pick_data.clicked.connect(self._pick_data_dir)
        reload_btn = QPushButton("刷新版本")
        reload_btn.clicked.connect(self._reload_versions)
        data_row = QHBoxLayout()
        data_row.addWidget(self.data_dir, stretch=1)
        data_row.addWidget(pick_data)
        data_row.addWidget(reload_btn)
        form.addRow("数据目录 (--data-dir):", _wrap(data_row))

        self.version = QComboBox()
        self.version.setEditable(True)
        form.addRow("版本 (--version):", self.version)

        self.output_dir = QLineEdit(str(default_output_dir()))
        pick_out = QPushButton("浏览…")
        pick_out.clicked.connect(self._pick_output_dir)
        out_row = QHBoxLayout()
        out_row.addWidget(self.output_dir, stretch=1)
        out_row.addWidget(pick_out)
        form.addRow("输出目录 (--output-dir):", _wrap(out_row))

        self.mysql = QCheckBox("MySQL")
        self.mysql.setChecked(True)
        self.postgresql = QCheckBox("PostgreSQL")
        self.postgresql.setChecked(True)
        dialect_row = QHBoxLayout()
        dialect_row.addWidget(self.mysql)
        dialect_row.addWidget(self.postgresql)
        dialect_row.addStretch(1)
        form.addRow("方言 (--dialect):", _wrap(dialect_row))

        self.batch = QSpinBox()
        self.batch.setRange(50, 5000)
        self.batch.setValue(500)
        form.addRow("批量 (--batch-size):", self.batch)

        self.no_csv = QCheckBox("跳过 CSV (--no-csv)")
        form.addRow(self.no_csv)

        root.addWidget(form_box)

        button_row = QHBoxLayout()
        self.start_btn = QPushButton("生成")
        self.start_btn.clicked.connect(self._start)
        self.open_btn = QPushButton("打开输出目录")
        self.open_btn.clicked.connect(self._open_output)
        self.open_btn.setEnabled(False)
        button_row.addStretch(1)
        button_row.addWidget(self.open_btn)
        button_row.addWidget(self.start_btn)
        root.addLayout(button_row)

        self.log = LogView()
        root.addWidget(self.log, stretch=1)

    def _pick_data_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择数据目录", self.data_dir.text())
        if path:
            self.data_dir.setText(path)
            self._reload_versions()

    def _pick_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择输出目录", self.output_dir.text())
        if path:
            self.output_dir.setText(path)

    def _reload_versions(self) -> None:
        self.version.clear()
        root = Path(self.data_dir.text() or "data")
        if not root.is_dir():
            return
        versions = sorted(
            p.name for p in root.iterdir()
            if p.is_dir() and (p / "province_index.json").exists()
        )
        for v in versions:
            self.version.addItem(v)
        if versions:
            self.version.setCurrentIndex(len(versions) - 1)

    def _collect_args(self) -> argparse.Namespace:
        dialects: list[str] = []
        if self.mysql.isChecked():
            dialects.append("mysql")
        if self.postgresql.isChecked():
            dialects.append("postgresql")
        return argparse.Namespace(
            data_dir=self.data_dir.text() or "data",
            version=self.version.currentText() or None,
            output_dir=self.output_dir.text() or "dist",
            batch_size=self.batch.value(),
            dialect=dialects or None,  # generate_sql treats None as "both"
            no_csv=self.no_csv.isChecked(),
        )

    def _start(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        args = self._collect_args()
        if not args.version:
            self.log.append("[错误] 未选择版本，先点「刷新版本」")
            return
        self._last_out_dir = Path(args.output_dir) / args.version
        self.log.clear()
        self.log.set_progress(0, 0)
        self.start_btn.setEnabled(False)
        self.open_btn.setEnabled(False)

        self._worker = GenerateWorker(args, self)
        self._worker.log.connect(self.log.append)
        self._worker.finished_ok.connect(self._on_done)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

    def _on_done(self) -> None:
        self.log.set_idle("完成")
        self.start_btn.setEnabled(True)
        self.open_btn.setEnabled(self._last_out_dir is not None and self._last_out_dir.exists())

    def _on_failed(self, msg: str) -> None:
        self.log.set_idle(f"失败：{msg[:40]}")
        self.start_btn.setEnabled(True)

    def _open_output(self) -> None:
        if self._last_out_dir and self._last_out_dir.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._last_out_dir)))


def _wrap(layout) -> QWidget:
    holder = QWidget()
    holder.setLayout(layout)
    return holder
