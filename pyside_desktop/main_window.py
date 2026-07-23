"""Main window: sidebar navigation with stacked pages."""

from __future__ import annotations

import sys

from PySide6.QtCore import QModelIndex, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from . import i18n
from .controller import HomeController, TrainingPrecision, kCustomPresetLabel

_TAB_KEYS = (
    "tab_model",
    "tab_data",
    "tab_train",
    "tab_monitor",
    "tab_export",
    "tab_settings",
    "tab_test",
)

_TAB_ICON_KEYS = (
    "model",
    "data",
    "train",
    "monitor",
    "export",
    "settings",
    "test",
)


def _ui_theme() -> dict[str, str]:
    if sys.platform == "darwin":
        return {
            "window": "rgba(241, 245, 251, 0.94)",
            "sidebar": "rgba(255, 255, 255, 0.58)",
            "content": "rgba(255, 255, 255, 0.56)",
            "header": "rgba(255, 255, 255, 0.66)",
            "surface": "rgba(255, 255, 255, 0.80)",
            "surface2": "rgba(248, 250, 255, 0.88)",
            "border": "rgba(214, 224, 235, 0.92)",
            "border_soft": "rgba(229, 236, 244, 0.84)",
            "text": "#102033",
            "text_strong": "#0f172a",
            "muted": "#64748b",
            "muted2": "#475569",
            "accent": "#0a84ff",
            "accent_dark": "#0066d6",
            "danger": "#ff3b30",
            "button_bg": "rgba(255, 255, 255, 0.76)",
            "button_hover": "rgba(246, 249, 253, 0.98)",
            "button_text": "#102033",
            "button_border": "rgba(207, 216, 228, 0.86)",
            "chip_bg": "rgba(248, 250, 255, 0.8)",
        }
    return {
        "window": "#eef1f7",
        "sidebar": "#f7f9fc",
        "content": "#ffffff",
        "header": "#ffffff",
        "surface": "#ffffff",
        "surface2": "#f8fbff",
        "border": "#dfe5ee",
        "border_soft": "#e4ebf3",
        "text": "#1f2937",
        "text_strong": "#0f172a",
        "muted": "#6b7280",
        "muted2": "#475569",
        "accent": "#1d4ed8",
        "accent_dark": "#1745be",
        "danger": "#dc2626",
        "button_bg": "#ffffff",
        "button_hover": "#f3f7fb",
        "button_text": "#1f2937",
        "button_border": "#d7dee8",
        "chip_bg": "#f3f6fb",
    }


def _ss(theme: dict[str, str]) -> str:
    return "\n".join(
        [
            f"QMainWindow, QWidget {{ background: {theme['window']}; color: {theme['text']}; }}",
            "QLabel { background: transparent; }",
            f"QFrame#sidebar {{ background: {theme['sidebar']}; border: 1px solid {theme['border']}; border-radius: 20px; }}",
            f"QFrame#contentShell {{ background: {theme['content']}; border: 1px solid {theme['border']}; border-radius: 20px; }}",
            f"QFrame#headerBar {{ background: {theme['header']}; border: 1px solid {theme['border']}; border-radius: 16px; }}",
            f"QFrame#bottomStatusBar {{ background: {theme['surface']}; border-top: 1px solid {theme['border']}; }}",
            "QFrame#sidebarFooter { background: transparent; border: none; }",
            f"QLabel#brandMark {{ background: {theme['accent']}; color: white; border-radius: 10px; font-size: 15px; font-weight: 700; }}",
            f"QLabel#pageTitle {{ color: {theme['text_strong']}; font-size: 19px; font-weight: 700; }}",
            f"QLabel#pageSubtitle {{ color: {theme['muted']}; font-size: 12px; }}",
            f"QLabel#statusChip {{ background: {theme['chip_bg']}; border: 1px solid {theme['border_soft']}; border-radius: 10px; color: {theme['muted2']}; padding: 8px 11px; font-size: 12px; font-weight: 600; }}",
            f"QLabel#statusDot {{ background: {theme['accent']}; border-radius: 4px; min-width: 8px; max-width: 8px; min-height: 8px; max-height: 8px; }}",
            f"QLabel#bottomStatusText {{ color: {theme['muted2']}; font-size: 12px; font-weight: 600; }}",
            f"QLabel#bottomStatusDivider {{ color: {theme['border']}; font-size: 12px; }}",
            "QListWidget#navList { background: transparent; border: none; outline: none; }",
            f"QListWidget#navList::item {{ background: transparent; color: {theme['muted2']}; border: 1px solid transparent; border-radius: 13px; padding: 10px 10px 10px 10px; margin: 2px 2px; min-height: 46px; font-size: 18px; font-weight: 750; }}",
            "QListWidget#navList::item:hover { background: #eef3fb; }",
            f"QListWidget#navList::item:selected {{ background: {theme['surface2']}; color: {theme['accent_dark']}; border: 1px solid {theme['border_soft']}; border-left: 4px solid {theme['accent']}; padding-left: 8px; }}",
            f"QGroupBox {{ font-weight: 600; border: 1px solid {theme['border_soft']}; border-radius: 14px; margin-top: 10px; padding: 12px; background: {theme['surface']}; }}",
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; color: {theme['muted2']}; font-size: 12px; font-weight: 700; }}",
            f"QLineEdit, QPlainTextEdit, QComboBox {{ background: {theme['surface']}; border: 1px solid {theme['button_border']}; border-radius: 12px; padding: 0 12px; min-height: 38px; font-size: 13px; color: {theme['text_strong']}; selection-background-color: {theme['accent']}; }}",
            "QLineEdit::placeholder, QPlainTextEdit::placeholder { color: #94a3b8; }",
            f"QLabel#fieldLabel {{ color: {theme['muted']}; font-size: 12px; font-weight: 600; padding: 4px 14px 4px 0; }}",
            f"QLabel#valueDisplay {{ color: {theme['text_strong']}; font-size: 14px; font-weight: 600; padding: 6px 0; background: transparent; }}",
            f"QLabel#hintDisplay {{ color: {theme['muted']}; padding: 4px 0; background: transparent; }}",
            f"QFrame#fieldPanel, QFrame#metricPanel {{ background: {theme['surface2']}; border: 1px solid {theme['border_soft']}; border-radius: 14px; }}",
            f"QPlainTextEdit#logPanel {{ background: {theme['surface2']}; border: 1px solid {theme['border_soft']}; border-radius: 12px; padding: 10px 12px; color: {theme['muted2']}; }}",
            "QPlainTextEdit#logPanel:focus { border: none; outline: none; }",
            f"QComboBox QAbstractItemView {{ background: {theme['surface']}; color: {theme['text']}; outline: 0; border: 1px solid {theme['button_border']}; padding: 4px; selection-background-color: {theme['accent']}; selection-color: #ffffff; }}",
            f"QPushButton {{ background: {theme['button_bg']}; color: {theme['button_text']}; border: 1px solid {theme['button_border']}; border-radius: 12px; padding: 0 12px; min-height: 38px; font-size: 13px; font-weight: 600; }}",
            f"QPushButton:hover {{ background: {theme['button_hover']}; }}",
            "QPushButton:disabled { background: rgba(243, 246, 250, 0.55); color: #94a3b8; }",
            f"QPushButton#primary {{ background: {theme['accent']}; color: white; border: 1px solid {theme['accent']}; }}",
            f"QPushButton#primary:hover {{ background: {theme['accent_dark']}; }}",
            f"QPushButton#secondary {{ background: {theme['button_bg']}; }}",
            f"QPushButton#secondary:checked {{ background: {theme['surface2']}; border: 1px solid {theme['border_soft']}; color: {theme['accent_dark']}; }}",
            f"QPushButton#green {{ background: {theme['accent']}; color: #ffffff; border: 1px solid {theme['accent']}; }}",
            f"QPushButton#red {{ background: {theme['danger']}; color: #ffffff; border: 1px solid {theme['danger']}; }}",
            f"QRadioButton {{ background: rgba(255, 255, 255, 0.42); border: 1px solid transparent; border-radius: 12px; color: {theme['text_strong']}; font-size: 14px; font-weight: 650; spacing: 8px; padding: 6px 16px 6px 12px; min-height: 32px; }}",
            f"QRadioButton:hover {{ background: {theme['button_hover']}; border: 1px solid {theme['border_soft']}; }}",
            f"QRadioButton:checked {{ background: rgba(10, 132, 255, 0.12); border: 1px solid rgba(10, 132, 255, 0.28); color: {theme['accent_dark']}; }}",
            f"QRadioButton::indicator {{ width: 14px; height: 14px; border-radius: 7px; border: 2px solid {theme['button_border']}; background: rgba(255, 255, 255, 0.92); }}",
            f"QRadioButton::indicator:hover {{ border: 2px solid {theme['accent']}; }}",
            f"QRadioButton::indicator:checked {{ border: 2px solid {theme['accent']}; background: {theme['accent']}; }}",
            "QTabWidget::pane { border: none; background: transparent; }",
            "QScrollArea { border: none; background: transparent; }",
        ]
    )


def tr(k: str, **p: str) -> str:
    return i18n.tr(k, **p)


def _nav_icon(kind: str, color: str, size: int = 20) -> QIcon:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(QColor(color))
    pen.setWidthF(2.3)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    s = float(size)
    m = 2.5
    if kind == "model":
        painter.drawRoundedRect(m + 1, m + 2, s - 2 * m - 2, s - 2 * m - 2, 2, 2)
        painter.drawLine(m + 1, m + 5, s - m - 1, m + 5)
        painter.drawLine(m + 3, m + 2, m + 3, s - m - 2)
    elif kind == "data":
        painter.drawEllipse(m + 1, m + 1.5, s - 2 * m - 2, 4)
        painter.drawLine(m + 1, m + 3.5, m + 1, s - m - 4)
        painter.drawLine(s - m - 1, m + 3.5, s - m - 1, s - m - 4)
        painter.drawEllipse(m + 1, s - m - 5.5, s - 2 * m - 2, 4)
        painter.drawLine(m + 1, s / 2, s - m - 1, s / 2)
        painter.drawLine(m + 1, s / 2 + 4, s - m - 1, s / 2 + 4)
    elif kind == "train":
        painter.drawLine(m + 2, m + 4, s - m - 2, m + 4)
        painter.drawLine(m + 2, s / 2, s - m - 2, s / 2)
        painter.drawLine(m + 2, s - m - 4, s - m - 2, s - m - 4)
        painter.drawEllipse(m + 3, m + 2.8, 3, 3)
        painter.drawEllipse(s - m - 6, s / 2 - 1.2, 3, 3)
        painter.drawEllipse(m + 6, s - m - 5.2, 3, 3)
    elif kind == "monitor":
        painter.drawRect(m + 1, m + 1.5, s - 2 * m - 2, s - 2 * m - 5)
        painter.drawLine(m + 3, s - m - 3, s - m - 3, s - m - 3)
        path = QPainterPath()
        path.moveTo(m + 3, s - m - 6)
        path.lineTo(m + 6, s / 2)
        path.lineTo(m + 9, s / 2 + 2)
        path.lineTo(s - m - 4, m + 5)
        painter.drawPath(path)
    elif kind == "export":
        painter.drawRect(m + 2, s - m - 7, s - 2 * m - 4, 3)
        painter.drawLine(s / 2, m + 2, s / 2, s - m - 6)
        painter.drawLine(s / 2, m + 2, s / 2 - 3, m + 5)
        painter.drawLine(s / 2, m + 2, s / 2 + 3, m + 5)
    elif kind == "settings":
        painter.drawEllipse(m + 4, m + 4, s - 2 * m - 8, s - 2 * m - 8)
        for a in range(0, 360, 60):
            path = QPainterPath()
            path.moveTo(s / 2, s / 2)
            if a == 0:
                path.lineTo(s / 2, m + 1.5)
            elif a == 60:
                path.lineTo(s - m - 2, m + 4.5)
            elif a == 120:
                path.lineTo(s - m - 2, s - m - 4.5)
            elif a == 180:
                path.lineTo(s / 2, s - m - 1.5)
            elif a == 240:
                path.lineTo(m + 2, s - m - 4.5)
            else:
                path.lineTo(m + 2, m + 4.5)
            painter.drawPath(path)
    elif kind == "test":
        painter.drawRoundedRect(m + 1.5, m + 2.5, s - 2 * m - 3, s - 2 * m - 6, 3, 3)
        painter.drawLine(m + 5, s - m - 4, m + 7, s - m - 1)
        painter.drawLine(m + 6, s / 2, s - m - 5, s / 2)
        painter.drawLine(m + 6, s / 2 + 3, s / 2, s / 2 + 3)
    painter.end()
    return QIcon(pm)


class _NoElideDelegate(QStyledItemDelegate):
    """Combo popup items still elide via QStyleOptionViewItem unless we override this."""

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex) -> None:  # noqa: N802
        super().initStyleOption(option, index)
        option.textElideMode = Qt.TextElideMode.ElideNone


class _WidePopupComboBox(QComboBox):
    """Widen the popup and disable middle ellipsis on macOS/Fusion combo lists."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        v = self.view()
        v.setTextElideMode(Qt.TextElideMode.ElideNone)
        v.setItemDelegate(_NoElideDelegate(v))

    def _popup_min_width(self) -> int:
        view = self.view()
        if self.count() <= 0:
            return self.width()
        fm = view.fontMetrics()
        tw = max(fm.boundingRect(self.itemText(i)).width() for i in range(self.count()))
        style = QApplication.style()
        sb = 0
        if style is not None:
            sb = style.pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent, None, self)
        # List padding (stylesheet) + item margins + scrollbar when shown
        return max(self.width(), tw + sb + 52)

    def showPopup(self) -> None:  # noqa: N802
        view = self.view()
        view.setTextElideMode(Qt.TextElideMode.ElideNone)
        mw = self._popup_min_width()
        view.setMinimumWidth(mw)
        super().showPopup()
        # Popup layout sometimes applies combobox width after show; re-apply next tick.
        QTimer.singleShot(0, lambda v=view, w=mw: (v.setMinimumWidth(w), v.updateGeometry()))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._ctrl = HomeController()
        self._ctrl.changed.connect(self.refresh)
        self._ctrl.toast.connect(self._on_toast)
        self._ui = _ui_theme()

        self.setWindowTitle(tr("app_title"))
        self.setMinimumSize(1200, 780)
        self.setStyleSheet(_ss(self._ui))
        if sys.platform == "darwin":
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._inputs: dict[str, QLineEdit] = {}
        self._tr_widgets: list[tuple[QWidget, str, str]] = []
        self._model_loading_dialog: QDialog | None = None
        self._model_loading_spinner: QLabel | None = None
        self._model_loading_label: QLabel | None = None
        self._model_loading_spinner_timer: QTimer | None = None
        self._model_loading_spinner_index = 0
        self._test_loading_dialog: QDialog | None = None
        self._test_loading_spinner: QLabel | None = None
        self._test_loading_label: QLabel | None = None
        self._test_loading_spinner_timer: QTimer | None = None
        self._test_loading_spinner_index = 0

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().hide()

        self._tab_model = self._wrap_scroll(self._page_model())
        self._tab_data = self._wrap_scroll(self._page_data())
        self._tab_train = self._wrap_scroll(self._page_train())
        self._tab_monitor = self._page_monitor()
        self._tab_export = self._wrap_scroll(self._page_export())
        self._tab_settings = self._wrap_scroll(self._page_settings())
        self._tab_test = self._wrap_scroll(self._page_test())

        for page, key in zip(
            (
                self._tab_model,
                self._tab_data,
                self._tab_train,
                self._tab_monitor,
                self._tab_export,
                self._tab_settings,
                self._tab_test,
            ),
            _TAB_KEYS,
        ):
            self.tabs.addTab(page, tr(key))
        self.tabs.currentChanged.connect(self._on_tab_changed)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(12)
        root.addWidget(body, 1)

        self._build_sidebar(body_layout)

        content = QWidget()
        content.setObjectName("contentShell")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 16, 18, 18)
        content_layout.setSpacing(12)
        body_layout.addWidget(content, 1)

        content_layout.addWidget(self.tabs, 1)

        self._build_bottom_status_bar(root)

        self._overlay = QLabel(self)
        self._overlay.setAlignment(Qt.AlignCenter)
        self._overlay.setStyleSheet(
            f"background: rgba(15,23,42,0.38); color: {self._ui['surface']}; font-size: 16px;"
        )
        self._overlay.hide()

        self.tabs.setCurrentIndex(0)
        self._sync_nav_selection(0)
        self._sync_shell_header()
        self._normalize_control_sizes()

        QTimer.singleShot(0, self._boot)
        self._sync_all_inputs_from_ctrl()
        self.refresh()

    def resizeEvent(self, e):  # noqa: N802
        super().resizeEvent(e)
        self._overlay.setGeometry(self.rect())

    def _apply_tr_widget(self, w: QWidget, key: str, mode: str) -> None:
        s = tr(key)
        if mode == "title":
            assert isinstance(w, QGroupBox)
            w.setTitle(s)
        elif mode == "placeholder":
            if isinstance(w, QPlainTextEdit):
                w.setPlaceholderText(s)
            elif isinstance(w, QLineEdit):
                w.setPlaceholderText(s)
        elif mode == "plain":
            if isinstance(w, QPlainTextEdit):
                w.setPlainText(s)
            elif isinstance(w, QLabel):
                w.setText(s)
        elif mode == "label_colon":
            assert isinstance(w, QLabel)
            w.setText(s + ":")
        else:
            assert isinstance(w, (QLabel, QPushButton))
            w.setText(s)

    def _tr_reg(self, w: QWidget, key: str, mode: str = "text") -> QWidget:
        self._tr_widgets.append((w, key, mode))
        self._apply_tr_widget(w, key, mode)
        return w

    def _retranslate_ui(self) -> None:
        for item in self._tr_widgets:
            self._apply_tr_widget(item[0], item[1], item[2])
        for i, key in enumerate(_TAB_KEYS):
            self.tabs.setTabText(i, tr(key))
        if hasattr(self, "nav_list"):
            for i, key in enumerate(_TAB_KEYS):
                item = self.nav_list.item(i)
                if item is not None:
                    item.setText(tr(key))
        if hasattr(self, "nav_list"):
            self._sync_nav_selection(self.tabs.currentIndex())
        if hasattr(self, "page_title"):
            self.page_title.setText(self.tabs.tabText(self.tabs.currentIndex()))
        if getattr(self, "_preset_buttons", None):
            for p, btn in self._preset_buttons:
                btn.setText(tr("preset_custom") if p.label == kCustomPresetLabel else p.label)

    def _boot(self) -> None:
        self._ctrl.ensure_repo_extracted()
        self._ctrl.detect_winget()
        self._ctrl.detect_nvidia_driver()
        self._ctrl.detect_uv()
        self._ctrl.detect_cuda_home()
        QTimer.singleShot(100, self._ctrl.check_environment)

    def _sync_all_inputs_from_ctrl(self) -> None:
        c = self._ctrl
        for attr in (
            "repo_path",
            "model_path",
            "data_path",
            "output_dir",
            "batch_size",
            "num_steps",
            "num_epochs",
            "ctx_len",
            "learning_rate",
        ):
            if attr in self._inputs:
                le = self._inputs[attr]
                v = getattr(c, attr)
                le.blockSignals(True)
                le.setText(str(v))
                le.blockSignals(False)

    def _on_tab_changed(self, idx: int) -> None:
        self._ctrl.set_tab_index(int(idx))
        self._sync_nav_selection(idx)
        self._sync_shell_header()

    def _sync_nav_selection(self, idx: int) -> None:
        if not hasattr(self, "nav_list"):
            return
        self.nav_list.blockSignals(True)
        self.nav_list.setCurrentRow(max(0, idx))
        self.nav_list.blockSignals(False)
        for i, icon_key in enumerate(_TAB_ICON_KEYS):
            item = self.nav_list.item(i)
            if item is not None:
                color = self._ui["accent"] if i == idx else self._ui["muted2"]
                item.setIcon(_nav_icon(icon_key, color))

    def _sync_shell_header(self) -> None:
        if hasattr(self, "page_title"):
            self.page_title.setText(self.tabs.tabText(self.tabs.currentIndex()))
        if hasattr(self, "page_subtitle"):
            self.page_subtitle.setText(self._ctrl.status)
        if hasattr(self, "gpu_label"):
            self.gpu_label.setText(tr("gpu_chip", v=self._ctrl.gpu_info) if self._ctrl.env_ready else self._ctrl.gpu_info)
        if hasattr(self, "status_label"):
            self.status_label.setText(self._ctrl.status)

    def _normalize_control_sizes(self) -> None:
        for le in self.findChildren(QLineEdit):
            le.setFixedHeight(38)
            le.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for cb in self.findChildren(QComboBox):
            cb.setFixedHeight(38)
            cb.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        if hasattr(self, "lang_combo"):
            self.lang_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for btn in self.findChildren(QPushButton):
            label = btn.text().strip()
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            if not label or label == "…":
                btn.setFixedSize(38, 38)
            else:
                btn.setMinimumHeight(38)
                btn.setMinimumWidth(0)
        for box in self.findChildren(QGroupBox):
            box.setContentsMargins(0, 0, 0, 0)

    def _build_sidebar(self, parent_layout: QHBoxLayout) -> None:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(232)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(10, 12, 10, 12)
        side_layout.setSpacing(8)

        brand = QWidget()
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(0, 2, 0, 10)
        brand_layout.setSpacing(8)
        mark = QLabel("ST")
        mark.setObjectName("brandMark")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setFixedSize(34, 34)
        brand_layout.addWidget(mark, 0, Qt.AlignmentFlag.AlignHCenter)
        brand_sub = QLabel("RWKV state tuning")
        brand_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_sub.setStyleSheet(
            f"font-size: 14px; font-weight: 700; color: {self._ui['text_strong']};"
        )
        brand_layout.addWidget(brand_sub)
        side_layout.addWidget(brand)

        self.nav_list = QListWidget()
        self.nav_list.setObjectName("navList")
        self.nav_list.setSpacing(0)
        self.nav_list.setFrameShape(QFrame.Shape.NoFrame)
        self.nav_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.nav_list.setIconSize(QSize(20, 20))
        self.nav_list.setUniformItemSizes(True)
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        for idx, key in enumerate(_TAB_KEYS):
            item = QListWidgetItem(tr(key))
            item.setData(Qt.ItemDataRole.UserRole, idx)
            item.setSizeHint(QSize(0, 46))
            item.setIcon(_nav_icon(_TAB_ICON_KEYS[idx], self._ui["muted2"]))
            self.nav_list.addItem(item)
        row_h = max(46, self.nav_list.sizeHintForRow(0) if self.nav_list.count() else 46)
        self.nav_list.setFixedHeight(row_h * self.nav_list.count() + 10)
        side_layout.addWidget(self.nav_list)

        side_layout.addStretch()

        footer = QFrame()
        footer.setObjectName("sidebarFooter")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(4, 0, 4, 2)
        footer_layout.setSpacing(8)

        self.lang_combo = _WidePopupComboBox()
        self.lang_combo.addItem("English", "en_US")
        self.lang_combo.addItem("简体中文", "zh_CN")
        self.lang_combo.addItem("繁體中文", "zh_TW")
        self.lang_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.lang_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        cur = i18n.current_locale()
        idx = max(0, self.lang_combo.findData(cur))
        self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentIndexChanged.connect(self._on_lang)
        footer_layout.addWidget(self.lang_combo)
        side_layout.addWidget(footer)

        parent_layout.addWidget(sidebar)

    def _build_bottom_status_bar(self, parent_layout: QVBoxLayout) -> None:
        bar = QFrame()
        bar.setObjectName("bottomStatusBar")
        bar.setFixedHeight(34)
        row = QHBoxLayout(bar)
        row.setContentsMargins(16, 0, 16, 0)
        row.setSpacing(10)

        dot = QLabel()
        dot.setObjectName("statusDot")
        row.addWidget(dot)

        self.status_label = QLabel()
        self.status_label.setObjectName("bottomStatusText")
        row.addWidget(self.status_label)

        sep = QLabel("|")
        sep.setObjectName("bottomStatusDivider")
        row.addWidget(sep)

        self.gpu_label = QLabel()
        self.gpu_label.setObjectName("bottomStatusText")
        row.addWidget(self.gpu_label)

        row.addStretch()
        parent_layout.addWidget(bar)

    def _on_nav_changed(self, idx: int) -> None:
        if idx >= 0 and self.tabs.currentIndex() != idx:
            self.tabs.setCurrentIndex(idx)

    def _on_toast(self, title: str, msg: str) -> None:
        QMessageBox.information(self, title, msg)

    def _update_summary_labels(self) -> None:
        if not hasattr(self, "sum_labels"):
            return
        c = self._ctrl

        def ns(x: str) -> str:
            return tr("value_not_set") if not x.strip() else x

        self.sum_labels["repo"].setText(ns(c.repo_path))
        self.sum_labels["model"].setText(ns(c.model_path))
        self.sum_labels["data"].setText(ns(c.data_path))
        self.sum_labels["out"].setText(c.output_dir)
        self.sum_labels["prec"].setText(c.precision_string.upper())
        pre = c.selected_preset
        self.sum_labels["spec"].setText(tr("preset_custom") if pre == kCustomPresetLabel else pre)
        self.sum_labels["embd"].setText(f"{c.n_embd} / {c.n_layer}")
        self.sum_labels["ctx"].setText(str(c.ctx_len))
        self.sum_labels["bse"].setText(f"{c.batch_size} / {c.num_steps} / {c.num_epochs}")
        self.sum_labels["lr"].setText(c.learning_rate)

    def _on_lang(self, _idx: int | None = None) -> None:
        loc = self.lang_combo.currentData()
        if loc:
            i18n.set_locale(str(loc))
            self._retranslate_ui()
            self._ctrl.reload_strings()
            self.refresh()

    def _wrap_scroll(self, inner: QWidget) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 18, 0)
        shell_layout.setSpacing(0)
        shell_layout.addWidget(inner)
        scroll.setWidget(shell)
        return scroll

    def _value_label(self, text: str = "", *, wrap: bool = False) -> QLabel:
        lb = QLabel(text)
        lb.setObjectName("valueDisplay")
        lb.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        if wrap:
            lb.setWordWrap(True)
        return lb

    def _field_label(self, key: str) -> QLabel:
        lb = QLabel()
        self._tr_reg(lb, key, "label_colon")
        lb.setObjectName("fieldLabel")
        return lb

    def _log_panel(
        self,
        *,
        mono: bool = False,
        max_height: int | None = None,
    ) -> QPlainTextEdit:
        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setObjectName("logPanel")
        if mono:
            view.setFont(
                QFont("Menlo", 11) if sys.platform == "darwin" else QFont("Consolas", 10)
            )
        if max_height is not None:
            view.setMaximumHeight(max_height)
        return view

    def _line(self, placeholder_key: str, attr: str, browse: str | None = None) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        le = QLineEdit()
        self._tr_reg(le, placeholder_key, "placeholder")
        self._inputs[attr] = le

        def sync(text: str) -> None:
            setattr(self._ctrl, attr, text)
            if attr == "model_path":
                self._ctrl.schedule_model_detect(text)

        le.textChanged.connect(sync)
        row.addWidget(le, 1)
        if browse:
            b = QPushButton("…")
            b.setFixedWidth(44)
            b.setObjectName("secondary")
            if browse == "file_pth":
                b.clicked.connect(self._pick_pth)
            elif browse == "file_jsonl":
                b.clicked.connect(self._pick_jsonl)
            elif browse == "dir":
                b.clicked.connect(self._pick_repo)
            elif browse == "out_dir":
                b.clicked.connect(self._pick_out)
            row.addWidget(b)
        return row

    def _line_widget(self, placeholder_key: str, attr: str, browse: str | None = None) -> QWidget:
        w = QWidget()
        w.setLayout(self._line(placeholder_key, attr, browse))
        return w

    def _section_panel(self, title_key: str) -> tuple[QFrame, QVBoxLayout]:
        panel = QFrame()
        panel.setObjectName("fieldPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        title = self._tr_reg(QLabel(), title_key)
        title.setStyleSheet(
            f"color: {self._ui['text_strong']}; font-size: 13px; font-weight: 700; padding: 0;"
        )
        layout.addWidget(title)
        return panel, layout

    def _page_model(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(16)

        header = QFrame()
        header.setObjectName("fieldPanel")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(14, 12, 14, 12)
        header_layout.setSpacing(10)

        header_title = QLabel(tr("model_file_path"))
        header_title.setStyleSheet(
            f"color: {self._ui['text_strong']}; font-size: 13px; font-weight: 700;"
        )
        header_layout.addWidget(header_title)

        fl = QFormLayout()
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setHorizontalSpacing(16)
        fl.setVerticalSpacing(8)
        fl.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        fl.addRow(
            self._field_label("label_pretrained_pth"),
            self._line_widget("hint_model_path", "model_path", "file_pth"),
        )
        self.detect_lbl = QLabel()
        self.detect_lbl.setStyleSheet(f"color: {self._ui['muted']}; font-size: 12px;")
        self.detect_lbl.setVisible(False)
        fl.addRow("", self.detect_lbl)
        header_layout.addLayout(fl)
        v.addWidget(header)

        presets = QGroupBox()
        self._tr_reg(presets, "model_specs_preset", "title")
        pv = QHBoxLayout(presets)
        pv.setContentsMargins(0, 0, 0, 0)
        pv.setSpacing(8)
        self._preset_buttons = []
        for p in self._ctrl.presets:
            lab = tr("preset_custom") if p.n_embd == 0 else p.label
            btn = QPushButton(lab)
            btn.setCheckable(True)
            btn.setObjectName("secondary")
            btn.clicked.connect(lambda _=False, pl=p.label: self._apply_preset(pl))
            self._preset_buttons.append((p, btn))
            pv.addWidget(btn)
        pv.addStretch()
        # Hide preset section on model tab as requested.
        presets.setVisible(False)

        adv, av = self._section_panel("modelargs_advanced")
        self.vocab_e = self._value_label()
        self.n_embd_e = self._value_label()
        self.n_layer_e = self._value_label()
        rows = (
            ("label_vocab_size", self.vocab_e),
            ("label_n_embd", self.n_embd_e),
            ("label_n_layer", self.n_layer_e),
        )
        af = QFormLayout()
        af.setContentsMargins(0, 0, 0, 0)
        af.setHorizontalSpacing(18)
        af.setVerticalSpacing(8)
        af.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        af.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        for label_key, value_widget in rows:
            value_widget.setStyleSheet(
                f"color: {self._ui['text_strong']}; font-size: 15px; font-weight: 700; padding: 2px 0;"
            )
            af.addRow(self._field_label(label_key), value_widget)
        av.addLayout(af)
        v.addWidget(adv)

        nx = QPushButton()
        self._tr_reg(nx, "next_data_config")
        nx.setObjectName("secondary")
        nx.setFixedWidth(184)
        nx.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        nx_row = QHBoxLayout()
        nx_row.setContentsMargins(0, 0, 0, 0)
        nx_row.addStretch()
        nx_row.addWidget(nx)
        v.addLayout(nx_row)
        v.addStretch()
        return w

    def _apply_preset(self, label: str) -> None:
        self._ctrl.apply_preset(label)
        for p, btn in self._preset_buttons:
            btn.setChecked(p.label == label)
        self.refresh_model_fields()

    def refresh_model_fields(self) -> None:
        c = self._ctrl
        self.vocab_e.setText(str(c.vocab_size))
        self.n_embd_e.setText(str(c.n_embd))
        self.n_layer_e.setText(str(c.n_layer))
        self.detect_lbl.setText(tr("reading_model_dims") if c.is_detecting_model else "")
        self.detect_lbl.setVisible(c.is_detecting_model)
        self._sync_model_loading_dialog(c.is_detecting_model)

    def _sync_model_loading_dialog(self, is_loading: bool) -> None:
        if not is_loading:
            if self._model_loading_dialog is not None:
                self._model_loading_dialog.close()
                self._model_loading_dialog = None
                self._model_loading_spinner = None
                self._model_loading_label = None
            if self._model_loading_spinner_timer is not None:
                self._model_loading_spinner_timer.stop()
                self._model_loading_spinner_timer = None
            return

        text = tr("reading_model_dims")
        if self._model_loading_dialog is None:
            dlg = QDialog(self)
            dlg.setWindowTitle(tr("reading_model_dims"))
            dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
            dlg.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
            dlg.setFixedSize(320, 140)
            lay = QVBoxLayout(dlg)
            spinner = QLabel("◐")
            spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spinner.setStyleSheet(f"font-size: 28px; color: {self._ui['accent']};")
            lay.addWidget(spinner)
            lab = QLabel(text)
            lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lab.setStyleSheet(f"font-size: 15px; color: {self._ui['muted2']};")
            lay.addWidget(lab)
            self._model_loading_dialog = dlg
            self._model_loading_spinner = spinner
            self._model_loading_label = lab
            self._model_loading_spinner_timer = QTimer(self)
            self._model_loading_spinner_timer.setInterval(120)
            self._model_loading_spinner_timer.timeout.connect(self._tick_model_loading_spinner)
            self._model_loading_spinner_timer.start()
            dlg.show()
            return

        self._model_loading_dialog.setWindowTitle(tr("reading_model_dims"))
        if self._model_loading_label is not None:
            self._model_loading_label.setText(text)

    def _tick_model_loading_spinner(self) -> None:
        if self._model_loading_spinner is None:
            return
        frames = ("◐", "◓", "◑", "◒")
        self._model_loading_spinner_index = (self._model_loading_spinner_index + 1) % len(frames)
        self._model_loading_spinner.setText(frames[self._model_loading_spinner_index])

    def _sync_test_loading_dialog(self, is_loading: bool) -> None:
        if not is_loading:
            if self._test_loading_dialog is not None:
                self._test_loading_dialog.close()
                self._test_loading_dialog = None
                self._test_loading_spinner = None
                self._test_loading_label = None
            if self._test_loading_spinner_timer is not None:
                self._test_loading_spinner_timer.stop()
                self._test_loading_spinner_timer = None
            return

        text = tr("btn_load_model_loading")
        if self._test_loading_dialog is None:
            dlg = QDialog(self)
            dlg.setWindowTitle(text)
            dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
            dlg.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
            dlg.setFixedSize(320, 140)
            lay = QVBoxLayout(dlg)
            spinner = QLabel("◐")
            spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spinner.setStyleSheet(f"font-size: 28px; color: {self._ui['accent']};")
            lay.addWidget(spinner)
            lab = QLabel(text)
            lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lab.setStyleSheet(f"font-size: 15px; color: {self._ui['muted2']};")
            lay.addWidget(lab)
            self._test_loading_dialog = dlg
            self._test_loading_spinner = spinner
            self._test_loading_label = lab
            self._test_loading_spinner_timer = QTimer(self)
            self._test_loading_spinner_timer.setInterval(120)
            self._test_loading_spinner_timer.timeout.connect(self._tick_test_loading_spinner)
            self._test_loading_spinner_timer.start()
            dlg.show()
            return

        self._test_loading_dialog.setWindowTitle(text)
        if self._test_loading_label is not None:
            self._test_loading_label.setText(text)

    def _tick_test_loading_spinner(self) -> None:
        if self._test_loading_spinner is None:
            return
        frames = ("◐", "◓", "◑", "◒")
        self._test_loading_spinner_index = (self._test_loading_spinner_index + 1) % len(frames)
        self._test_loading_spinner.setText(frames[self._test_loading_spinner_index])

    def _pick_pth(self) -> None:
        p, _ = QFileDialog.getOpenFileName(self, tr("dialog_pick_model_pth"), "", "*.pth;;All (*)")
        if p:
            self._ctrl.model_path = p
            if "model_path" in self._inputs:
                self._inputs["model_path"].setText(p)
                self._ctrl.schedule_model_detect(p)

    def _pick_jsonl(self) -> None:
        p, _ = QFileDialog.getOpenFileName(
            self, tr("dialog_pick_train_jsonl"), "", "*.jsonl *.json;;All (*)"
        )
        if p:
            self._ctrl.data_path = p
            if "data_path" in self._inputs:
                self._inputs["data_path"].setText(p)

    def _pick_repo(self) -> None:
        p = QFileDialog.getExistingDirectory(self, tr("dialog_pick_repo"))
        if p:
            self._ctrl.repo_path = p
            if "repo_path" in self._inputs:
                self._inputs["repo_path"].setText(p)
            self._ctrl.check_repo()

    def _pick_out(self) -> None:
        p = QFileDialog.getExistingDirectory(self, tr("dialog_pick_output_dir"))
        if p:
            self._ctrl.output_dir = p
            if "output_dir" in self._inputs:
                self._inputs["output_dir"].setText(p)

    def _pick_python_env(self) -> None:
        p = QFileDialog.getExistingDirectory(self, tr("dialog_pick_python_env"))
        if p:
            self._ctrl.select_python_env_dir(p)

    def _page_data(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(16)
        v.addWidget(self._tr_reg(QLabel(), "train_repo_desc"))

        repo, rl = self._section_panel("train_repo")
        rl.addWidget(self._tr_reg(QLabel(), "label_repo_path"))
        rl.addLayout(self._line("hint_repo_path_default", "repo_path", "dir"))
        hb = QHBoxLayout()
        chk = QPushButton()
        self._tr_reg(chk, "btn_check_path")
        chk.setObjectName("secondary")
        chk.clicked.connect(self._ctrl.check_repo)
        hb.addWidget(chk)
        hb.addStretch()
        rl.addLayout(hb)
        self.repo_log_view = self._log_panel(max_height=120)
        self._tr_reg(self.repo_log_view, "repo_log_placeholder", "placeholder")
        rl.addWidget(self.repo_log_view)
        v.addWidget(repo)

        dt, dl = self._section_panel("train_data")
        dl.addWidget(self._tr_reg(QLabel(), "label_jsonl_path"))
        dl.addLayout(self._line("hint_jsonl_pick", "data_path", "file_jsonl"))
        dl.addWidget(self._tr_reg(QLabel(), "data_format_title"))
        fmt = self._tr_reg(QLabel(), "data_format_example_line", "plain")
        fmt.setStyleSheet(f"color: {self._ui['accent']}; font-family: monospace;")
        fmt.setWordWrap(True)
        fmt.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        dl.addWidget(fmt)
        v.addWidget(dt)

        od, ol = self._section_panel("output_dir_section")
        ol.addLayout(self._line("hint_output_dir", "output_dir", "out_dir"))
        v.addWidget(od)

        nx = QPushButton()
        self._tr_reg(nx, "next_train_params")
        nx.setObjectName("secondary")
        nx.setFixedWidth(180)
        nx.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        nx_row = QHBoxLayout()
        nx_row.addStretch()
        nx_row.addWidget(nx)
        v.addLayout(nx_row)
        return w

    def _page_train(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(16)

        hp, hg = self._section_panel("train_hyperparams")
        g = QGridLayout()
        g.setContentsMargins(0, 0, 0, 0)
        g.setHorizontalSpacing(14)
        g.setVerticalSpacing(12)
        self._add_num_row(g, 0, 0, "label_batch_size", "batch_size")
        self._add_num_row(g, 0, 2, "label_num_steps", "num_steps")
        self._add_num_row(g, 1, 0, "label_num_epochs", "num_epochs")
        self._add_text_row(g, 1, 2, "label_lr", "learning_rate")
        self._add_num_row(g, 2, 0, "label_ctx_len", "ctx_len")
        hg.addLayout(g)
        v.addWidget(hp)

        prec, ph = self._section_panel("label_train_precision")
        radio_row = QHBoxLayout()
        radio_row.setContentsMargins(0, 0, 16, 0)
        radio_row.setSpacing(12)
        self._prec_buttons: list[tuple[TrainingPrecision, QRadioButton]] = []
        self._prec_group = QButtonGroup(w)
        self._prec_group.setExclusive(True)
        for p in TrainingPrecision:
            b = QRadioButton(p.value.upper())
            b.setMinimumWidth(92)
            b.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            b.toggled.connect(lambda checked=False, x=p: checked and self._set_prec(x))
            self._prec_group.addButton(b)
            self._prec_buttons.append((p, b))
            radio_row.addWidget(b)
        radio_row.addStretch()
        ph.addLayout(radio_row)
        v.addWidget(prec)

        sm, sg = self._section_panel("config_summary")
        sf = QFormLayout()
        sf.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        sf.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.sum_labels = {}
        for key, lab_key in [
            ("repo", "summary_repo"),
            ("model", "summary_model_file"),
            ("data", "summary_data_file"),
            ("out", "summary_output_dir"),
            ("prec", "summary_precision"),
            ("spec", "summary_model_spec"),
            ("embd", "summary_embd_layer"),
            ("ctx", "summary_ctx_len"),
            ("bse", "summary_batch_steps_epochs"),
            ("lr", "summary_lr"),
        ]:
            lb = self._value_label(wrap=True)
            sf.addRow(self._field_label(lab_key), lb)
            self.sum_labels[key] = lb
        sg.addLayout(sf)
        v.addWidget(sm)

        row = QHBoxLayout()
        self.train_btn = QPushButton()
        self._tr_reg(self.train_btn, "train_start")
        self.train_btn.setObjectName("primary")
        self.train_btn.setFixedWidth(200)
        self.train_btn.clicked.connect(self._start_training_and_open_monitor)
        row.addStretch()
        row.addWidget(self.train_btn)
        v.addLayout(row)
        v.addWidget(self._tr_reg(QLabel(), "train_hint_footer"))
        return w

    def _add_num_row(self, g: QGridLayout, r: int, c: int, title_key: str, attr: str) -> None:
        lw = QLabel()
        self._tr_reg(lw, title_key)
        g.addWidget(lw, r, c)
        le = QLineEdit()
        self._inputs[attr] = le
        le.textChanged.connect(
            lambda t, a=attr: self._set_num_from_line(a, t)
        )
        g.addWidget(le, r, c + 1)

    def _add_text_row(self, g: QGridLayout, r: int, c: int, title_key: str, attr: str) -> None:
        lw = QLabel()
        self._tr_reg(lw, title_key)
        g.addWidget(lw, r, c)
        le = QLineEdit()
        self._inputs[attr] = le
        le.textChanged.connect(lambda t, a=attr: setattr(self._ctrl, a, t))
        g.addWidget(le, r, c + 1)

    def _set_num_from_line(self, attr: str, text: str) -> None:
        try:
            v = int(text)
            if v > 0:
                setattr(self._ctrl, attr, v)
        except ValueError:
            pass

    def _set_prec(self, p: TrainingPrecision) -> None:
        self._ctrl.set_precision(p)
        for pr, btn in getattr(self, "_prec_buttons", []):
            btn.setChecked(pr == p)

    def _start_training_and_open_monitor(self) -> None:
        self._ctrl.start_training()
        # If training actually starts, switch to Monitor tab immediately.
        if self._ctrl.is_training:
            self.tabs.setCurrentIndex(3)

    def _page_monitor(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setSpacing(18)
        hb = QHBoxLayout()
        self.mon_badge = QLabel()
        hb.addWidget(self.mon_badge)
        hb.addStretch()
        self.mon_stop_btn = QPushButton()
        self._tr_reg(self.mon_stop_btn, "train_btn_stop")
        self.mon_stop_btn.setObjectName("red")
        self.mon_stop_btn.clicked.connect(self._ctrl.stop_training)
        hb.addWidget(self.mon_stop_btn)
        self.mon_export_btn = QPushButton()
        self._tr_reg(self.mon_export_btn, "monitor_export_loss_jsonl")
        self.mon_export_btn.setObjectName("secondary")
        self.mon_export_btn.clicked.connect(self._export_loss)
        hb.addWidget(self.mon_export_btn)
        self.mon_chart_btn = QPushButton()
        self._tr_reg(self.mon_chart_btn, "monitor_view_loss_chart")
        self.mon_chart_btn.setObjectName("secondary")
        self.mon_chart_btn.clicked.connect(self._loss_chart)
        hb.addWidget(self.mon_chart_btn)
        cl = QPushButton()
        self._tr_reg(cl, "monitor_clear_log")
        cl.setObjectName("secondary")
        cl.clicked.connect(self._clear_train_log)
        hb.addWidget(cl)
        v.addLayout(hb)
        self.log_view = self._log_panel(mono=True)
        self._tr_reg(self.log_view, "monitor_log_placeholder", "placeholder")
        v.addWidget(self.log_view, 1)
        return w

    def _clear_train_log(self) -> None:
        self._ctrl.training_log = ""
        self._ctrl._log_lines.clear()
        self._ctrl._log_current_line = ""
        self.refresh()

    def _export_loss(self) -> None:
        d = QFileDialog.getExistingDirectory(self, tr("dialog_pick_export_dir"))
        if d:
            self._ctrl.export_loss_log(d)

    def _loss_chart(self) -> None:
        try:
            from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
        except ImportError:
            QMessageBox.information(self, tr("tip"), "QtCharts not available.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(tr("monitor_loss_curve_title"))
        dlg.resize(720, 460)
        lay = QVBoxLayout(dlg)
        series = QLineSeries()
        chart = QChart()
        chart.addSeries(series)
        axis_x = QValueAxis()
        axis_x.setTitleText("steps")
        axis_x.setLabelFormat("%d")
        axis_y = QValueAxis()
        axis_y.setTitleText("loss")
        axis_y.setLabelFormat("%.4f")

        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        chart.legend().hide()

        def refresh_chart() -> None:
            losses = self._ctrl.loss_history
            series.clear()
            step = max(1, len(losses) // 400)
            for i in range(0, len(losses), step):
                series.append(i, losses[i])

            axis_x.setRange(0, max(1, len(losses) - 1))
            min_loss = min(losses) if losses else 0.0
            max_loss = max(losses) if losses else 1.0
            if min_loss == max_loss:
                min_loss = max(0.0, min_loss - 1.0)
                max_loss += 1.0
            axis_y.setRange(min_loss, max_loss)

        refresh_chart()
        refresh_timer = QTimer(dlg)
        refresh_timer.setInterval(1000)
        refresh_timer.timeout.connect(refresh_chart)
        refresh_timer.start()
        dlg.finished.connect(refresh_timer.stop)

        v = QChartView(chart)
        lay.addWidget(v)
        bb = QDialogButtonBox(QDialogButtonBox.Close)
        bb.rejected.connect(dlg.close)
        lay.addWidget(bb)
        dlg.exec()

    def _page_export(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(16)

        dir_panel, dir_layout = self._section_panel("output_dir_section")
        self.exp_dir_lbl = QLabel()
        self.exp_dir_lbl.setWordWrap(True)
        dir_layout.addWidget(self.exp_dir_lbl)
        v.addWidget(dir_panel)

        hb = QHBoxLayout()
        rf = QPushButton()
        self._tr_reg(rf, "export_refresh_list")
        rf.setObjectName("secondary")
        rf.clicked.connect(self._ctrl.refresh_output_files)
        hb.addWidget(rf)
        self.exp_export_btn = QPushButton()
        self._tr_reg(self.exp_export_btn, "monitor_export_loss_jsonl")
        self.exp_export_btn.setObjectName("secondary")
        self.exp_export_btn.clicked.connect(self._export_loss)
        hb.addWidget(self.exp_export_btn)
        hb.addStretch()
        v.addLayout(hb)

        self.file_list = self._log_panel(mono=True)
        self._tr_reg(self.file_list, "export_no_files_hint", "placeholder")
        files_panel, files_layout = self._section_panel("export_output_files")
        files_layout.addWidget(self.file_list, 1)
        v.addWidget(files_panel, 1)

        usage_box, ul = self._section_panel("export_usage_title")
        ul.addWidget(self._tr_reg(QLabel(), "export_usage_body"))
        v.addWidget(usage_box)
        return w

    def _page_settings(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(16)
        v.addWidget(self._tr_reg(QLabel(), "settings_system_intro"))

        # ── System Basics ─────────────────────────────────────────────────────
        sb, sg = self._section_panel("settings_system_basics")

        if sys.platform == "win32":
            # winget row (Windows only)
            wh = QHBoxLayout()
            self.winget_lbl = QLabel()
            wh.addWidget(self.winget_lbl, 1)
            wh.addStretch()
            sg.addLayout(wh)

        # UV row
        uh = QHBoxLayout()
        self.uv_lbl = QLabel()
        uh.addWidget(self.uv_lbl, 1)
        if sys.platform == "win32":
            self.uv_install_btn = QPushButton()
            self._tr_reg(self.uv_install_btn, "btn_install")
            self.uv_install_btn.setObjectName("secondary")
            self.uv_install_btn.clicked.connect(self._ctrl.install_uv)
            uh.addWidget(self.uv_install_btn)
        sg.addLayout(uh)

        # NVIDIA driver row
        nh = QHBoxLayout()
        self.nvidia_lbl = QLabel()
        nh.addWidget(self.nvidia_lbl, 1)
        if sys.platform == "win32":
            self.nvidia_install_btn = QPushButton()
            self._tr_reg(self.nvidia_install_btn, "btn_install")
            self.nvidia_install_btn.setObjectName("secondary")
            self.nvidia_install_btn.clicked.connect(self._ctrl.install_nvidia_driver)
            nh.addWidget(self.nvidia_install_btn)
        sg.addLayout(nh)

        self.sys_log = self._log_panel(max_height=80)
        sg.addWidget(self.sys_log)
        v.addWidget(sb)

        # ── CUDA ──────────────────────────────────────────────────────────────
        cg, cl = self._section_panel("cuda_section_title")
        self._cuda_home_le = QLineEdit(self._ctrl.cuda_home)
        self._cuda_home_le.textChanged.connect(lambda t: setattr(self._ctrl, "cuda_home", t))
        self._tr_reg(self._cuda_home_le, "cuda_dir_label", "placeholder")
        cl.addWidget(self._tr_reg(QLabel(), "cuda_dir_label"))
        cl.addWidget(self._cuda_home_le)
        brow = QHBoxLayout()
        ad = QPushButton()
        self._tr_reg(ad, "btn_auto_detect")
        ad.setObjectName("secondary")
        ad.clicked.connect(self._ctrl.detect_cuda_home)
        brow.addWidget(ad)
        if sys.platform == "win32":
            self.cuda_install_btn = QPushButton()
            self._tr_reg(self.cuda_install_btn, "btn_install_cuda")
            self.cuda_install_btn.setObjectName("secondary")
            self.cuda_install_btn.clicked.connect(self._ctrl.install_cuda_winget)
            brow.addWidget(self.cuda_install_btn)
        brow.addStretch()
        cl.addLayout(brow)
        self.cuda_log = self._log_panel(max_height=100)
        cl.addWidget(self.cuda_log)
        v.addWidget(cg)

        # ── Environment ───────────────────────────────────────────────────────
        eg, el = self._section_panel("env_section_title")
        ebrow = QHBoxLayout()
        chk = QPushButton()
        self._tr_reg(chk, "env_check_env")
        chk.setObjectName("secondary")
        chk.clicked.connect(self._ctrl.check_environment)
        ebrow.addWidget(chk)
        pick_env = QPushButton()
        self._tr_reg(pick_env, "btn_select_python_env")
        pick_env.setObjectName("secondary")
        pick_env.clicked.connect(self._pick_python_env)
        ebrow.addWidget(pick_env)
        self.env_install_btn = QPushButton()
        self._tr_reg(self.env_install_btn, "btn_install_env")
        self.env_install_btn.setObjectName("primary")
        self.env_install_btn.clicked.connect(self._ctrl.install_environment)
        ebrow.addWidget(self.env_install_btn)
        ebrow.addStretch()
        el.addLayout(ebrow)
        self.env_log = self._log_panel()
        el.addWidget(self.env_log)
        v.addWidget(eg)

        if sys.platform == "win32":
            # ── Build Tools (Windows only) ────────────────────────────────────
            btg, btl = self._section_panel("build_tools_section")
            bth = QHBoxLayout()
            self.ninja_lbl = QLabel()
            self.msvc_lbl = QLabel()
            bth.addWidget(self.ninja_lbl)
            bth.addWidget(self.msvc_lbl)
            bth.addStretch()
            self.bt_install_btn = QPushButton()
            self._tr_reg(self.bt_install_btn, "btn_install_build_tools")
            self.bt_install_btn.setObjectName("secondary")
            self.bt_install_btn.clicked.connect(self._ctrl.install_build_tools)
            bth.addWidget(self.bt_install_btn)
            btl.addLayout(bth)
            self.build_tools_log_view = self._log_panel(max_height=80)
            btl.addWidget(self.build_tools_log_view)
            v.addWidget(btg)

        v.addStretch()
        return w

    def _page_test(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(16)

        load_grp, lg = self._section_panel("test_model_load_title")

        # model .pth
        lg.addWidget(self._tr_reg(QLabel(), "label_pretrained_pth"))
        mh = QHBoxLayout()
        self._test_model_le = QLineEdit()
        self._tr_reg(self._test_model_le, "hint_model_path", "placeholder")
        self._test_model_le.textChanged.connect(lambda t: setattr(self._ctrl, "test_model_path", t))
        mh.addWidget(self._test_model_le, 1)
        mb = QPushButton("…")
        mb.setFixedWidth(44)
        mb.setObjectName("secondary")
        mb.clicked.connect(self._pick_test_model)
        mh.addWidget(mb)
        lg.addLayout(mh)

        # tokenizer
        lg.addWidget(self._tr_reg(QLabel(), "label_tokenizer_path"))
        th = QHBoxLayout()
        self._test_tok_le = QLineEdit()
        self._tr_reg(self._test_tok_le, "hint_tokenizer", "placeholder")
        self._test_tok_le.textChanged.connect(lambda t: setattr(self._ctrl, "test_tokenizer_path", t))
        th.addWidget(self._test_tok_le, 1)
        tb = QPushButton("…")
        tb.setFixedWidth(44)
        tb.setObjectName("secondary")
        tb.clicked.connect(self._pick_test_tokenizer)
        th.addWidget(tb)
        lg.addLayout(th)

        # state file
        lg.addWidget(self._tr_reg(QLabel(), "label_state_path"))
        sh = QHBoxLayout()
        self._test_state_le = QLineEdit()
        self._tr_reg(self._test_state_le, "hint_state_file", "placeholder")
        self._test_state_le.textChanged.connect(lambda t: setattr(self._ctrl, "test_state_path", t))
        sh.addWidget(self._test_state_le, 1)
        stb = QPushButton("…")
        stb.setFixedWidth(44)
        stb.setObjectName("secondary")
        stb.clicked.connect(self._pick_test_state)
        sh.addWidget(stb)
        lg.addLayout(sh)

        brow = QHBoxLayout()
        load_btn = QPushButton()
        self._tr_reg(load_btn, "btn_load_model")
        load_btn.setObjectName("primary")
        load_btn.setFixedWidth(140)
        load_btn.clicked.connect(self._ctrl.load_rwkv_test_model)
        brow.addWidget(load_btn)
        clr = QPushButton()
        self._tr_reg(clr, "btn_clear_chat")
        clr.setObjectName("secondary")
        clr.clicked.connect(self._ctrl.clear_rwkv_chat)
        brow.addWidget(clr)
        brow.addStretch()
        self.test_status_lbl = QLabel(self._ctrl.rwkv_status)
        self.test_status_lbl.setStyleSheet(f"color: {self._ui['muted']};")
        brow.addWidget(self.test_status_lbl)
        lg.addLayout(brow)
        v.addWidget(load_grp)

        chat_grp, cl = self._section_panel("test_chat_title")
        self.test_chat_view = self._log_panel(mono=True)
        self._tr_reg(self.test_chat_view, "test_chat_empty", "placeholder")
        cl.addWidget(self.test_chat_view, 1)

        ph = QHBoxLayout()
        self.test_prompt_le = QLineEdit()
        self._tr_reg(self.test_prompt_le, "test_prompt_hint", "placeholder")
        self.test_prompt_le.returnPressed.connect(self._send_test_prompt)
        ph.addWidget(self.test_prompt_le, 1)
        send_btn = QPushButton()
        self._tr_reg(send_btn, "btn_send")
        send_btn.setObjectName("primary")
        send_btn.setFixedWidth(120)
        send_btn.clicked.connect(self._send_test_prompt)
        ph.addWidget(send_btn)
        cl.addLayout(ph)
        v.addWidget(chat_grp, 1)
        return w

    def _pick_test_model(self) -> None:
        p, _ = QFileDialog.getOpenFileName(self, tr("dialog_pick_model_pth"), "", "*.pth;;All (*)")
        if p:
            self._ctrl.test_model_path = p
            self._test_model_le.setText(p)

    def _pick_test_tokenizer(self) -> None:
        p, _ = QFileDialog.getOpenFileName(self, tr("snackbar_dialog_pick_tokenizer"), "", "*.json *.txt;;All (*)")
        if p:
            self._ctrl.test_tokenizer_path = p
            self._test_tok_le.setText(p)

    def _pick_test_state(self) -> None:
        p, _ = QFileDialog.getOpenFileName(self, tr("snackbar_dialog_pick_state"), "", "*.pth;;All (*)")
        if p:
            self._ctrl.test_state_path = p
            self._test_state_le.setText(p)

    def _send_test_prompt(self) -> None:
        txt = self.test_prompt_le.text().strip()
        if not txt:
            return
        self.test_prompt_le.clear()
        self._ctrl.test_prompt = txt
        self._ctrl.send_rwkv_prompt()
        self.refresh()

    def refresh(self) -> None:
        c = self._ctrl
        environment_fully_ready = c.env_ready and (
            sys.platform != "win32" or c.build_tools_fully_ready
        )
        self.setWindowTitle(tr("app_title"))
        self._sync_shell_header()
        if hasattr(self, "nav_hint"):
            self.nav_hint.setText(c.status)

        # ── CUDA log ──────────────────────────────────────────────────────────
        if hasattr(self, "cuda_log"):
            self.cuda_log.setPlainText((c.cuda_detect_log + "\n" + c.cuda_install_log).strip())
        if hasattr(self, "_cuda_home_le"):
            le = self._cuda_home_le
            if le.text() != c.cuda_home:
                le.blockSignals(True)
                le.setText(c.cuda_home)
                le.blockSignals(False)

        # ── System basics labels ───────────────────────────────────────────────
        if hasattr(self, "winget_lbl"):
            ok = "✓" if c.winget_installed else "✗"
            self.winget_lbl.setText(f"winget  {ok}")
        if hasattr(self, "uv_lbl"):
            ok = "✓" if c.uv_installed else "✗"
            self.uv_lbl.setText(f"uv  {ok}")
            if hasattr(self, "uv_install_btn"):
                self.uv_install_btn.setVisible(not c.uv_installed)
                self.uv_install_btn.setEnabled(not c.is_uv_installing)
        if hasattr(self, "nvidia_lbl"):
            ok = "✓" if c.nvidia_driver_installed else "✗"
            self.nvidia_lbl.setText(f"NVIDIA Driver  {ok}")
            if hasattr(self, "nvidia_install_btn"):
                self.nvidia_install_btn.setVisible(not c.nvidia_driver_installed)
        if hasattr(self, "sys_log"):
            self.sys_log.setPlainText(
                tr("log_env_ready_display")
                if environment_fully_ready
                else c.uv_install_log
            )
        if hasattr(self, "cuda_install_btn"):
            self.cuda_install_btn.setVisible(not c.cuda_installed)
            self.cuda_install_btn.setEnabled(not c.is_cuda_installing)

        # ── Build tools ───────────────────────────────────────────────────────
        if hasattr(self, "ninja_lbl"):
            self.ninja_lbl.setText(f"ninja  {'✓' if c.ninja_on_path else '✗'}")
        if hasattr(self, "msvc_lbl"):
            self.msvc_lbl.setText(f"MSVC cl  {'✓' if c.msvc_cl_on_path else '✗'}")
        if hasattr(self, "build_tools_log_view"):
            self.build_tools_log_view.setPlainText(
                tr("log_env_ready_display")
                if environment_fully_ready
                else c.build_tools_log
            )
        if hasattr(self, "bt_install_btn"):
            self.bt_install_btn.setVisible(not c.build_tools_fully_ready)
            self.bt_install_btn.setEnabled(not c.is_build_tools_installing)

        # ── Env log ───────────────────────────────────────────────────────────
        if hasattr(self, "env_log"):
            self.env_log.setPlainText((c.check_log + "\n" + c.install_log).strip())
        if hasattr(self, "env_install_btn"):
            self.env_install_btn.setVisible(not c.env_ready)
            self.env_install_btn.setEnabled(not c.is_installing and not c.is_checking)

        # ── Export ────────────────────────────────────────────────────────────
        if hasattr(self, "exp_dir_lbl"):
            self.exp_dir_lbl.setText(c.output_dir)
        if hasattr(self, "file_list"):
            self.file_list.setPlainText("\n".join(c.output_files))
        if hasattr(self, "exp_export_btn"):
            self.exp_export_btn.setEnabled(bool(c.loss_history))

        # ── Monitor ───────────────────────────────────────────────────────────
        if hasattr(self, "mon_badge"):
            self.mon_badge.setText(
                tr("monitor_badge_training") if c.is_training else tr("monitor_badge_idle")
            )
        if hasattr(self, "mon_stop_btn"):
            self.mon_stop_btn.setVisible(c.is_training)
        if hasattr(self, "mon_export_btn"):
            self.mon_export_btn.setEnabled(bool(c.loss_history))
        if hasattr(self, "mon_chart_btn"):
            self.mon_chart_btn.setEnabled(bool(c.loss_history))

        # ── Train tab buttons ─────────────────────────────────────────────────
        if hasattr(self, "train_btn"):
            self.train_btn.setEnabled(not c.is_training)
            self.train_btn.setText(tr("train_in_progress") if c.is_training else tr("train_start"))

        self.refresh_model_fields()
        self._update_summary_labels()
        if hasattr(self, "_prec_buttons"):
            for p, btn in self._prec_buttons:
                btn.setChecked(p == c.precision)

        # ── Log view ──────────────────────────────────────────────────────────
        if hasattr(self, "log_view"):
            cur = self.log_view.toPlainText()
            if cur != c.training_log:
                self.log_view.setPlainText(c.training_log)
                sb = self.log_view.verticalScrollBar()
                sb.setValue(sb.maximum())
        if hasattr(self, "repo_log_view"):
            self.repo_log_view.setPlainText(c.repo_log)

        # ── Test tab ──────────────────────────────────────────────────────────
        self._sync_test_loading_dialog(c.is_rwkv_loading)
        if hasattr(self, "test_status_lbl"):
            self.test_status_lbl.setText(c.rwkv_status)
        if hasattr(self, "test_chat_view"):
            lines = []
            for msg in c.rwkv_messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                lines.append(f"[{role.upper()}] {content}")
            self.test_chat_view.setPlainText("\n\n".join(lines))

        # ── Overlay ───────────────────────────────────────────────────────────
        if c.is_cloning_repo:
            self._overlay.setText(tr("clone_repo_initializing"))
            self._overlay.show()
            self._overlay.raise_()
        else:
            self._overlay.hide()
