"""Centralized Qt stylesheet for the xzqh GUI.

Hand-crafted dark theme — no third-party dependency, applies on top of
Qt's built-in ``Fusion`` style for consistent rendering across platforms.

Design tokens:
  - background  #0d0f12 (deep space slate-black)
  - panel       #12151c (sleek card panel)
  - elevated    #1c202b (hover / active panels)
  - border      #2b303c (subtle borders)
  - divider     #21242c (clean dividers)
  - text        #f3f4f6 (pure white text)
  - muted       #8a93a6 (elegant slate grey)
  - accent      #3b82f6 (electric blue)
  - accent-glow #6366f1 (indigo/violet glow)
  - success     #10b981 (emerald green)
  - danger      #ef4444 (crimson red)
"""

from __future__ import annotations

DARK_QSS = """
* {
    color: #f3f4f6;
    font-family: "Segoe UI", "SF Pro Display", "PingFang SC", "Microsoft YaHei UI", sans-serif;
    font-size: 13px;
}

QMainWindow, QWidget {
    background-color: #0d0f12;
}

/* ----------------- Tabs ----------------- */
QTabWidget::pane {
    border: 1px solid #222631;
    border-radius: 8px;
    background-color: #12151c;
    top: -1px;
}
QTabBar::tab {
    background: transparent;
    color: #8a93a6;
    padding: 10px 24px;
    margin-right: 4px;
    border: none;
    border-bottom: 2px solid transparent;
    font-weight: 500;
}
QTabBar::tab:hover {
    color: #f3f4f6;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 6px 6px 0 0;
}
QTabBar::tab:selected {
    color: #f3f4f6;
    border-bottom: 2px solid #3b82f6;
    font-weight: 600;
    background: rgba(59, 130, 246, 0.08);
    border-radius: 6px 6px 0 0;
}

/* ----------------- Group boxes ----------------- */
QGroupBox {
    border: 1px solid #222631;
    border-radius: 8px;
    margin-top: 16px;
    padding: 18px 14px 14px 14px;
    background-color: #12151c;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 2px 8px;
    color: #3b82f6;
    background-color: #0d0f12;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}

/* ----------------- Labels ----------------- */
QLabel {
    background: transparent;
}

/* ----------------- Buttons ----------------- */
QPushButton {
    background-color: #1c202b;
    border: 1px solid #2b303c;
    border-radius: 6px;
    padding: 7px 18px;
    color: #f3f4f6;
    min-width: 72px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #242938;
    border-color: #3f4659;
}
QPushButton:pressed {
    background-color: #161922;
}
QPushButton:disabled {
    color: #4b5263;
    background-color: #12151c;
    border-color: #1c202b;
}
QPushButton[primary="true"] {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #6366f1);
    border: none;
    color: #ffffff;
    font-weight: 600;
}
QPushButton[primary="true"]:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #818cf8);
}
QPushButton[primary="true"]:pressed {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #4f46e5);
}
QPushButton[primary="true"]:disabled {
    background-color: #1d2b45;
    border: none;
    color: #718096;
}
QPushButton[danger="true"] {
    background-color: #1c1515;
    border: 1px solid #ef4444;
    color: #fca5a5;
    font-weight: 500;
}
QPushButton[danger="true"]:hover {
    background-color: #3b1818;
    color: #ffffff;
}
QPushButton[danger="true"]:pressed {
    background-color: #271010;
}

/* ----------------- Inputs ----------------- */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit {
    background-color: #08090c;
    border: 1px solid #2b303c;
    border-radius: 6px;
    padding: 7px 10px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QComboBox:focus, QPlainTextEdit:focus {
    border-color: #3b82f6;
}
QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled,
QComboBox:disabled, QPlainTextEdit:disabled {
    color: #4b5263;
    background-color: #0f1115;
    border-color: #1c202b;
}

QComboBox::drop-down {
    width: 26px;
    border: none;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #8a93a6;
    width: 0;
    height: 0;
    margin-right: 10px;
}
QComboBox::down-arrow:hover {
    border-top-color: #f3f4f6;
}
QComboBox QAbstractItemView {
    background-color: #12151c;
    border: 1px solid #2b303c;
    border-radius: 6px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
    outline: 0;
    padding: 4px;
}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 16px;
}

/* ----------------- Checkbox ----------------- */
QCheckBox {
    spacing: 10px;
    background: transparent;
    font-weight: 500;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #2b303c;
    background-color: #08090c;
}
QCheckBox::indicator:hover {
    border-color: #3b82f6;
}
QCheckBox::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
    image: none;
}
QCheckBox::indicator:checked:hover {
    background-color: #6366f1;
    border-color: #6366f1;
}

/* ----------------- Progress bar ----------------- */
QProgressBar {
    background-color: #08090c;
    border: 1px solid #2b303c;
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    font-weight: 600;
    height: 20px;
}
QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #6366f1);
    border-radius: 5px;
}

/* ----------------- Log / Plain text ----------------- */
QPlainTextEdit {
    font-family: "Consolas", "Cascadia Mono", "Menlo", monospace;
    font-size: 12px;
    color: #e2e8f0;
    background-color: #060709;
    border: 1px solid #2b303c;
    border-radius: 6px;
    line-height: 150%;
}

/* ----------------- Tree view ----------------- */
QTreeWidget, QTreeView {
    background-color: #08090c;
    alternate-background-color: #0e1117;
    border: 1px solid #2b303c;
    border-radius: 6px;
    show-decoration-selected: 1;
    outline: 0;
}
QTreeWidget::item, QTreeView::item {
    padding: 6px 4px;
    border: none;
    color: #e2e8f0;
}
QTreeWidget::item:hover, QTreeView::item:hover {
    background-color: rgba(255, 255, 255, 0.04);
}
QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: rgba(59, 130, 246, 0.2);
    color: #ffffff;
    font-weight: 600;
}
QHeaderView::section {
    background-color: #12151c;
    color: #8a93a6;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #21242c;
    border-bottom: 1px solid #21242c;
    font-weight: 600;
}
QHeaderView::section:last {
    border-right: none;
}

/* ----------------- Scrollbars ----------------- */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2b303c;
    min-height: 24px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #3f4659;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
    border: none;
    height: 0;
}
QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #2b303c;
    min-width: 24px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #3f4659;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
    border: none;
    width: 0;
}

/* ----------------- Splitter ----------------- */
QSplitter::handle {
    background-color: #1a1e26;
}
QSplitter::handle:horizontal {
    width: 4px;
}
QSplitter::handle:vertical {
    height: 4px;
}

/* ----------------- Tool tips ----------------- */
QToolTip {
    background-color: #12151c;
    color: #f3f4f6;
    border: 1px solid #2b303c;
    border-radius: 4px;
    padding: 6px 10px;
}

/* ----------------- Form layout label color ----------------- */
QFormLayout QLabel {
    color: #8a93a6;
    font-weight: 500;
}
"""
