"""Centralized Qt stylesheet for the xzqh GUI.

Hand-crafted dark theme — no third-party dependency, applies on top of
Qt's built-in ``Fusion`` style for consistent rendering across platforms.

Design tokens:
  - background  #1f2024
  - panel       #25272d
  - elevated    #2d3038
  - border      #3a3e47
  - divider     #2a2c33
  - text        #e6e8eb
  - muted       #a4a8b3
  - accent      #4c8bf5
  - accent-hi   #6aa1ff
  - success     #3fb950
  - danger      #e54b4b
"""

from __future__ import annotations

DARK_QSS = """
* {
    color: #e6e8eb;
    font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC", sans-serif;
    font-size: 13px;
}

QMainWindow, QWidget {
    background-color: #1f2024;
}

/* ----------------- Tabs ----------------- */
QTabWidget::pane {
    border: 1px solid #2a2c33;
    border-radius: 6px;
    background-color: #25272d;
    top: -1px;
}
QTabBar::tab {
    background: transparent;
    color: #a4a8b3;
    padding: 9px 22px;
    margin-right: 2px;
    border: none;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:hover {
    color: #e6e8eb;
}
QTabBar::tab:selected {
    color: #e6e8eb;
    border-bottom: 2px solid #4c8bf5;
}

/* ----------------- Group boxes ----------------- */
QGroupBox {
    border: 1px solid #3a3e47;
    border-radius: 6px;
    margin-top: 14px;
    padding: 14px 12px 10px 12px;
    background-color: #25272d;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #a4a8b3;
    background-color: #1f2024;
}

/* ----------------- Labels ----------------- */
QLabel {
    background: transparent;
}

/* ----------------- Buttons ----------------- */
QPushButton {
    background-color: #2d3038;
    border: 1px solid #3a3e47;
    border-radius: 5px;
    padding: 6px 16px;
    color: #e6e8eb;
    min-width: 64px;
}
QPushButton:hover {
    background-color: #353841;
    border-color: #4a4e58;
}
QPushButton:pressed {
    background-color: #282b32;
}
QPushButton:disabled {
    color: #5a5f6a;
    background-color: #25272d;
    border-color: #2f323a;
}
QPushButton[primary="true"] {
    background-color: #4c8bf5;
    border: 1px solid #4c8bf5;
    color: #ffffff;
    font-weight: 600;
}
QPushButton[primary="true"]:hover {
    background-color: #6aa1ff;
    border-color: #6aa1ff;
}
QPushButton[primary="true"]:pressed {
    background-color: #3d77d8;
    border-color: #3d77d8;
}
QPushButton[primary="true"]:disabled {
    background-color: #324868;
    border-color: #324868;
    color: #8a99b3;
}
QPushButton[danger="true"] {
    background-color: #2d3038;
    border: 1px solid #e54b4b;
    color: #ff7575;
}
QPushButton[danger="true"]:hover {
    background-color: #3a2e2e;
}

/* ----------------- Inputs ----------------- */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit {
    background-color: #1a1b1f;
    border: 1px solid #3a3e47;
    border-radius: 5px;
    padding: 6px 8px;
    selection-background-color: #4c8bf5;
    selection-color: #ffffff;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QComboBox:focus, QPlainTextEdit:focus {
    border-color: #4c8bf5;
}
QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled,
QComboBox:disabled, QPlainTextEdit:disabled {
    color: #5a5f6a;
    background-color: #1d1e22;
}

QComboBox::drop-down {
    width: 22px;
    border: none;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #a4a8b3;
    width: 0;
    height: 0;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #25272d;
    border: 1px solid #3a3e47;
    selection-background-color: #4c8bf5;
    selection-color: #ffffff;
    outline: 0;
}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 16px;
}

/* ----------------- Checkbox ----------------- */
QCheckBox {
    spacing: 8px;
    background: transparent;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #4a4e58;
    background-color: #1a1b1f;
}
QCheckBox::indicator:hover {
    border-color: #6a6f7a;
}
QCheckBox::indicator:checked {
    background-color: #4c8bf5;
    border-color: #4c8bf5;
    image: none;
}

/* ----------------- Progress bar ----------------- */
QProgressBar {
    background-color: #1a1b1f;
    border: 1px solid #3a3e47;
    border-radius: 5px;
    text-align: center;
    color: #e6e8eb;
    height: 18px;
}
QProgressBar::chunk {
    background-color: #4c8bf5;
    border-radius: 4px;
}

/* ----------------- Log / Plain text ----------------- */
QPlainTextEdit {
    font-family: "Consolas", "Cascadia Mono", "Menlo", monospace;
    font-size: 12px;
    color: #d4d7dc;
    background-color: #15161a;
    border-radius: 5px;
}

/* ----------------- Tree view ----------------- */
QTreeWidget, QTreeView {
    background-color: #1a1b1f;
    alternate-background-color: #1d1e23;
    border: 1px solid #3a3e47;
    border-radius: 5px;
    show-decoration-selected: 1;
    outline: 0;
}
QTreeWidget::item, QTreeView::item {
    padding: 4px 2px;
    border: none;
}
QTreeWidget::item:hover, QTreeView::item:hover {
    background-color: #2a2c33;
}
QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: #324868;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #25272d;
    color: #a4a8b3;
    padding: 6px 8px;
    border: none;
    border-right: 1px solid #2a2c33;
    border-bottom: 1px solid #2a2c33;
    font-weight: 600;
}
QHeaderView::section:last {
    border-right: none;
}

/* ----------------- Scrollbars ----------------- */
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #3a3e47;
    min-height: 24px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #4a4e58;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
    border: none;
    height: 0;
}
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #3a3e47;
    min-width: 24px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background: #4a4e58;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
    border: none;
    width: 0;
}

/* ----------------- Splitter ----------------- */
QSplitter::handle {
    background-color: #2a2c33;
}
QSplitter::handle:horizontal {
    width: 6px;
}
QSplitter::handle:vertical {
    height: 6px;
}

/* ----------------- Tool tips ----------------- */
QToolTip {
    background-color: #25272d;
    color: #e6e8eb;
    border: 1px solid #3a3e47;
    padding: 4px 8px;
}

/* ----------------- Form layout label color ----------------- */
QFormLayout QLabel {
    color: #a4a8b3;
}
"""
