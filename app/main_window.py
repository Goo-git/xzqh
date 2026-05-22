"""Main window: QTabWidget with three tabs."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget

from .tabs.browse_tab import BrowseTab
from .tabs.fetch_tab import FetchTab
from .tabs.generate_tab import GenerateTab


class BrandHeader(QWidget):
    """A sleek brand banner at the top of the application."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("BrandHeader")
        self.setFixedHeight(68)
        self.setStyleSheet(
            "QWidget#BrandHeader {"
            "  background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #12151c, stop:1 #0d0f12);"
            "  border-bottom: 1px solid #222631;"
            "}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        # Left branding texts
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)

        title = QLabel("中国行政区划数据集 · xzqh Suite")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        subtitle = QLabel("民政部官方数据一键抓取、多版本增量生成 SQL/CSV 与多级数据可视化面板")
        subtitle.setStyleSheet("font-size: 12px; color: #8a93a6;")

        left_layout.addWidget(title)
        left_layout.addWidget(subtitle)

        # Right status badge
        badge = QLabel("PRO ACTIVE")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedSize(86, 22)
        badge.setStyleSheet(
            "QLabel {"
            "  background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #6366f1);"
            "  color: #ffffff;"
            "  font-size: 10px;"
            "  font-weight: bold;"
            "  border-radius: 4px;"
            "  letter-spacing: 0.5px;"
            "}"
        )

        layout.addWidget(left_widget, stretch=1)
        layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignVCenter)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("行政区划工具 · xzqh GUI")
        self.resize(1200, 800)

        # Main central layout wrapper
        central = QWidget(self)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top brand banner
        header = BrandHeader(self)
        main_layout.addWidget(header)

        # Spacious container for Tab Widget
        tab_container = QWidget()
        container_layout = QVBoxLayout(tab_container)
        container_layout.setContentsMargins(20, 16, 20, 20)
        container_layout.setSpacing(0)

        tabs = QTabWidget(self)
        tabs.setDocumentMode(True)
        tabs.setMovable(False)
        tabs.addTab(FetchTab(self), "  抓取数据  ")
        tabs.addTab(GenerateTab(self), "  生成 SQL/CSV  ")
        tabs.addTab(BrowseTab(self), "  数据预览  ")

        container_layout.addWidget(tabs)
        main_layout.addWidget(tab_container, stretch=1)

        self.setCentralWidget(central)
        self.statusBar().showMessage("就绪")
