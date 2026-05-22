"""Browse tab: lazy-load tree viewer for an existing data version."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.paths import default_data_dir

LEVEL_NAMES = {0: "全国", 1: "省级", 2: "地级", 3: "县级", 4: "乡级"}

# Item user-data role storing the raw JSON dict.
_NODE_ROLE = Qt.ItemDataRole.UserRole
# Marker to detect a not-yet-expanded placeholder child.
_LAZY_MARKER = "__lazy__"


class BrowseTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._reload_versions()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        # Top: data dir + version selector
        top = QHBoxLayout()
        self.data_dir = QLineEdit(str(default_data_dir()))
        pick = QPushButton("浏览…")
        pick.clicked.connect(self._pick_data_dir)
        reload_btn = QPushButton("刷新")
        reload_btn.clicked.connect(self._reload_versions)
        self.version = QComboBox()
        self.version.currentTextChanged.connect(self._on_version_changed)
        top.addWidget(QLabel("数据目录"))
        top.addWidget(self.data_dir, stretch=1)
        top.addWidget(pick)
        top.addWidget(QLabel("版本"))
        top.addWidget(self.version)
        top.addWidget(reload_btn)
        root.addLayout(top)

        # Filter
        filter_row = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("按名称或 code 过滤当前展开的节点…")
        self.filter_edit.textChanged.connect(self._apply_filter)
        filter_row.addWidget(QLabel("过滤"))
        filter_row.addWidget(self.filter_edit, stretch=1)
        root.addLayout(filter_row)

        # Tree + detail
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["名称", "代码", "类型"])
        self.tree.setColumnWidth(0, 280)
        self.tree.setColumnWidth(1, 110)
        self.tree.itemExpanded.connect(self._on_expanded)
        self.tree.currentItemChanged.connect(self._on_current_changed)
        splitter.addWidget(self.tree)

        self.detail = QLabel("（未选择节点）")
        self.detail.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.detail.setMargin(10)
        self.detail.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        splitter.addWidget(self.detail)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, stretch=1)

    # ----- version handling -----

    def _pick_data_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择数据目录", self.data_dir.text())
        if path:
            self.data_dir.setText(path)
            self._reload_versions()

    def _reload_versions(self) -> None:
        prev = self.version.currentText()
        self.version.blockSignals(True)
        self.version.clear()
        root = Path(self.data_dir.text() or "data")
        if root.is_dir():
            versions = sorted(
                p.name for p in root.iterdir()
                if p.is_dir() and (p / "province_index.json").exists()
            )
            for v in versions:
                self.version.addItem(v)
            if prev in versions:
                self.version.setCurrentText(prev)
            elif versions:
                self.version.setCurrentIndex(len(versions) - 1)
        self.version.blockSignals(False)
        self._on_version_changed(self.version.currentText())

    def _on_version_changed(self, version: str) -> None:
        self.tree.clear()
        if not version:
            return
        version_dir = Path(self.data_dir.text() or "data") / version
        index_path = version_dir / "province_index.json"
        if not index_path.is_file():
            return
        try:
            province_index = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            self.detail.setText(f"读取 province_index.json 失败：{exc}")
            return

        for entry in province_index:
            file_rel = entry.get("file")
            if not file_rel:
                continue
            province_path = version_dir / file_rel
            if not province_path.is_file():
                continue
            try:
                tree = json.loads(province_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            self._add_node(self.tree.invisibleRootItem(), tree, depth_limit=3)

    # ----- tree population -----

    def _add_node(self, parent: QTreeWidgetItem, node: dict, depth_limit: int) -> QTreeWidgetItem:
        item = QTreeWidgetItem(parent)
        item.setText(0, str(node.get("name") or ""))
        item.setText(1, str(node.get("code") or ""))
        item.setText(2, str(node.get("type") or ""))
        item.setData(0, _NODE_ROLE, node)

        children = node.get("children") or []
        if not children:
            return item
        if depth_limit > 0:
            for child in children:
                self._add_node(item, child, depth_limit - 1)
        else:
            # Defer: add a placeholder so the disclosure arrow shows.
            placeholder = QTreeWidgetItem(item)
            placeholder.setText(0, _LAZY_MARKER)
        return item

    def _on_expanded(self, item: QTreeWidgetItem) -> None:
        # If first child is a lazy placeholder, materialize real children now.
        if item.childCount() == 1 and item.child(0).text(0) == _LAZY_MARKER:
            item.removeChild(item.child(0))
            node = item.data(0, _NODE_ROLE)
            if isinstance(node, dict):
                for child in node.get("children") or []:
                    self._add_node(item, child, depth_limit=0)

    # ----- detail panel -----

    def _on_current_changed(self, item: QTreeWidgetItem | None, _prev: QTreeWidgetItem | None) -> None:
        if item is None:
            self.detail.setText("（未选择节点）")
            return
        node = item.data(0, _NODE_ROLE)
        if not isinstance(node, dict):
            self.detail.setText("（无详情）")
            return
        parent = item.parent()
        parent_node = parent.data(0, _NODE_ROLE) if parent is not None else None
        parent_str = "（顶层）"
        if isinstance(parent_node, dict):
            parent_str = f"{parent_node.get('code')} {parent_node.get('name')}"
        level = int(node.get("level") or 0)
        children = node.get("children") or []
        self.detail.setText(
            "<b>详情</b><br>"
            f"<b>code:</b> {node.get('code')}<br>"
            f"<b>name:</b> {node.get('name')}<br>"
            f"<b>level:</b> {level} ({LEVEL_NAMES.get(level, '?')})<br>"
            f"<b>type:</b> {node.get('type') or '-'}<br>"
            f"<b>parent:</b> {parent_str}<br>"
            f"<b>children:</b> {len(children)}"
        )

    # ----- filtering -----

    def _apply_filter(self, text: str) -> None:
        needle = text.strip().lower()

        def walk(item: QTreeWidgetItem) -> bool:
            visible_self = (
                not needle
                or needle in item.text(0).lower()
                or needle in item.text(1).lower()
            )
            any_child_visible = False
            for i in range(item.childCount()):
                if walk(item.child(i)):
                    any_child_visible = True
            show = visible_self or any_child_visible
            item.setHidden(not show)
            return show

        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            walk(root.child(i))
