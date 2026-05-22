"""Main window: QTabWidget with three tabs."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from .tabs.browse_tab import BrowseTab
from .tabs.fetch_tab import FetchTab
from .tabs.generate_tab import GenerateTab


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("行政区划工具 · xzqh GUI")
        self.resize(1100, 720)

        tabs = QTabWidget(self)
        tabs.addTab(FetchTab(self), "抓取数据")
        tabs.addTab(GenerateTab(self), "生成 SQL/CSV")
        tabs.addTab(BrowseTab(self), "数据预览")
        self.setCentralWidget(tabs)
