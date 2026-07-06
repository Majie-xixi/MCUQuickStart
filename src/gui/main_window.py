"""Main window for MCUQuickStart."""
from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.chip_db import ChipDatabase
from src.core.i18n import I18n
from src.core.project_generator import ProjectGenerator
from src.core.project_validator import ProjectValidator
from src.core.sdk_manager import SDKManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(860, 780)
        self.resize(960, 820)

        self._i18n = I18n(Path(__file__).parent.parent / "resources" / "i18n")
        self._i18n.set_language("en")
        self._theme = "light"

        self._sdk = SDKManager()
        self._sdk.load_config()
        self._chip_db = ChipDatabase(Path(__file__).parent.parent / "resources" / "chips")
        self._chip_db.load()
        self._gen = ProjectGenerator(
            Path(__file__).parent.parent / "resources" / "templates",
            self._sdk,
        )
        self._validator = ProjectValidator()

        self._build_ui()
        self._apply_theme()
        self._retranslate_ui()
        self._populate_families()

    def _tr(self, key: str, **kwargs) -> str:
        return self._i18n.get(key, **kwargs)

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("page")
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(10)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        self._title_label = QLabel("MCUQuickStart")
        self._title_label.setObjectName("appTitle")
        self._status_label = QLabel("Ready")
        self._status_label.setObjectName("statusText")
        title_box.addWidget(self._title_label)
        title_box.addWidget(self._status_label)
        header.addLayout(title_box)
        header.addStretch()

        self._about_btn = QPushButton()
        self._about_btn.setObjectName("secondaryButton")
        self._about_btn.setMinimumWidth(72)
        self._about_btn.clicked.connect(self._show_about)
        header.addWidget(self._about_btn)

        self._help_btn = QPushButton()
        self._help_btn.setObjectName("secondaryButton")
        self._help_btn.setMinimumWidth(72)
        self._help_btn.clicked.connect(self._show_help)
        header.addWidget(self._help_btn)

        self._theme_label = QLabel()
        self._theme_label.setObjectName("fieldLabel")
        header.addWidget(self._theme_label)

        self._theme_combo = QComboBox()
        self._theme_combo.setMinimumWidth(108)
        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        header.addWidget(self._theme_combo)

        self._lang_label = QLabel()
        self._lang_label.setObjectName("fieldLabel")
        header.addWidget(self._lang_label)

        self._lang_combo = QComboBox()
        self._lang_combo.setMinimumWidth(112)
        self._lang_combo.addItems(["Chinese", "English"])
        self._lang_combo.setCurrentText("English")
        self._lang_combo.currentTextChanged.connect(self._on_lang_changed)
        header.addWidget(self._lang_combo)
        layout.addLayout(header)

        main_grid = QVBoxLayout()
        main_grid.setSpacing(10)
        layout.addLayout(main_grid)

        self._sdk_group = QFrame()
        self._sdk_group.setObjectName("card")
        self._sdk_group.setFixedHeight(112)
        sdk_layout = QVBoxLayout(self._sdk_group)
        sdk_layout.setContentsMargins(20, 14, 20, 14)
        sdk_layout.setSpacing(8)
        self._sdk_title = QLabel()
        self._sdk_title.setObjectName("cardTitle")
        sdk_layout.addWidget(self._sdk_title)
        self._sdk_tip = QLabel()
        self._sdk_tip.setObjectName("hintText")
        self._sdk_tip.setWordWrap(True)
        sdk_layout.addWidget(self._sdk_tip)

        root_row = QHBoxLayout()
        root_row.setSpacing(8)
        self._root_label = QLabel()
        self._root_label.setObjectName("fieldLabel")
        root_row.addWidget(self._root_label)
        self._sdk_root = QLineEdit(self._sdk.get_path("SDK_ROOT"))
        self._sdk_root.setMinimumWidth(260)
        root_row.addWidget(self._sdk_root, 1)
        self._root_btn = QPushButton()
        self._root_btn.setObjectName("secondaryButton")
        self._root_btn.setMinimumWidth(104)
        self._root_btn.clicked.connect(self._browse_sdk)
        root_row.addWidget(self._root_btn)
        sdk_layout.addLayout(root_row)
        main_grid.addWidget(self._sdk_group)

        self._proj_group = QFrame()
        self._proj_group.setObjectName("card")
        self._proj_group.setFixedHeight(190)
        proj_card_layout = QVBoxLayout(self._proj_group)
        proj_card_layout.setContentsMargins(20, 14, 20, 14)
        proj_card_layout.setSpacing(8)
        self._proj_title = QLabel()
        self._proj_title.setObjectName("cardTitle")
        proj_card_layout.addWidget(self._proj_title)

        proj_layout = QGridLayout()
        proj_layout.setHorizontalSpacing(10)
        proj_layout.setVerticalSpacing(8)
        proj_layout.setColumnStretch(1, 1)
        proj_layout.setColumnStretch(3, 1)
        proj_card_layout.addLayout(proj_layout)

        self._family_label = QLabel()
        self._family_label.setObjectName("fieldLabel")
        self._family_combo = QComboBox()
        self._family_combo.currentTextChanged.connect(self._on_family_changed)
        self._chip_label = QLabel()
        self._chip_label.setObjectName("fieldLabel")
        self._chip_combo = QComboBox()
        self._name_label = QLabel()
        self._name_label.setObjectName("fieldLabel")
        self._proj_name = QLineEdit("MyProject")
        self._out_label = QLabel()
        self._out_label.setObjectName("fieldLabel")
        self._output_dir = QLineEdit(str(Path.home() / "Desktop"))
        self._out_btn = QPushButton()
        self._out_btn.setObjectName("secondaryButton")
        self._out_btn.setMinimumWidth(104)
        self._out_btn.clicked.connect(self._browse_output)
        self._hxtal_label = QLabel()
        self._hxtal_label.setObjectName("fieldLabel")
        self._hxtal_combo = QComboBox()
        self._hxtal_combo.addItems(["8 MHz", "25 MHz"])
        self._hxtal_combo.setCurrentText("8 MHz")

        proj_layout.addWidget(self._family_label, 0, 0)
        proj_layout.addWidget(self._family_combo, 0, 1)
        proj_layout.addWidget(self._chip_label, 0, 2)
        proj_layout.addWidget(self._chip_combo, 0, 3)
        proj_layout.addWidget(self._name_label, 1, 0)
        proj_layout.addWidget(self._proj_name, 1, 1)
        proj_layout.addWidget(self._hxtal_label, 1, 2)
        proj_layout.addWidget(self._hxtal_combo, 1, 3)
        proj_layout.addWidget(self._out_label, 2, 0)
        proj_layout.addWidget(self._output_dir, 2, 1, 1, 2)
        proj_layout.addWidget(self._out_btn, 2, 3)
        main_grid.addWidget(self._proj_group)

        option_row = QHBoxLayout()
        option_row.setSpacing(10)
        main_grid.addLayout(option_row)

        self._tmpl_group = QFrame()
        self._tmpl_group.setObjectName("card")
        self._tmpl_group.setFixedHeight(118)
        tmpl_layout = QVBoxLayout(self._tmpl_group)
        tmpl_layout.setContentsMargins(20, 14, 20, 14)
        tmpl_layout.setSpacing(6)
        self._tmpl_title = QLabel()
        self._tmpl_title.setObjectName("cardTitle")
        tmpl_layout.addWidget(self._tmpl_title)
        self._tmpl_empty = QRadioButton()
        self._tmpl_empty.setChecked(True)
        self._tmpl_led = QRadioButton()
        self._tmpl_uart = QRadioButton()
        tmpl_layout.addWidget(self._tmpl_empty)
        tmpl_layout.addWidget(self._tmpl_led)
        tmpl_layout.addWidget(self._tmpl_uart)
        option_row.addWidget(self._tmpl_group)

        self._lib_group = QFrame()
        self._lib_group.setObjectName("card")
        self._lib_group.setFixedHeight(118)
        lib_layout = QVBoxLayout(self._lib_group)
        lib_layout.setContentsMargins(20, 14, 20, 14)
        lib_layout.setSpacing(6)
        self._lib_title = QLabel()
        self._lib_title.setObjectName("cardTitle")
        lib_layout.addWidget(self._lib_title)
        self._lib_freertos = QCheckBox()
        self._lib_rtt_nano = QCheckBox()
        self._lib_gcc = QCheckBox()
        lib_layout.addWidget(self._lib_freertos)
        lib_layout.addWidget(self._lib_rtt_nano)
        lib_layout.addWidget(self._lib_gcc)
        option_row.addWidget(self._lib_group)

        self._lib_freertos.toggled.connect(self._on_rtos_toggled)
        self._lib_rtt_nano.toggled.connect(self._on_rtos_toggled)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setVisible(False)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(7)
        action_row.addWidget(self._progress, 1)

        self._gen_btn = QPushButton()
        self._gen_btn.setObjectName("primaryButton")
        self._gen_btn.setMinimumHeight(40)
        self._gen_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._gen_btn.clicked.connect(self._on_generate)
        action_row.addWidget(self._gen_btn)
        layout.addLayout(action_row)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("separator")
        layout.addWidget(separator)

        log_header = QHBoxLayout()
        self._log_title = QLabel()
        self._log_title.setObjectName("sectionTitle")
        log_header.addWidget(self._log_title)
        log_header.addStretch()
        self._clear_log_btn = QPushButton()
        self._clear_log_btn.setObjectName("secondaryButton")
        self._clear_log_btn.setMinimumWidth(76)
        self._clear_log_btn.clicked.connect(self._clear_log)
        log_header.addWidget(self._clear_log_btn)
        layout.addLayout(log_header)

        self._log = QTextEdit()
        self._log.setObjectName("logView")
        self._log.setReadOnly(True)
        self._log.setMinimumHeight(120)
        layout.addWidget(self._log, 1)

    def _apply_theme(self):
        chevron = (
            Path(__file__).parent.parent / "resources" / "icons" / "chevron-down.svg"
        ).as_posix()
        if self._theme == "light":
            qss = """
            QWidget#page {
                background: #f6f8fb;
                color: #17202b;
                font-family: "Segoe UI", "Microsoft YaHei UI", Arial, sans-serif;
                font-size: 13px;
            }
            QLabel#appTitle {
                color: #101828;
                font-size: 26px;
                font-weight: 700;
            }
            QLabel#statusText, QLabel#hintText {
                color: #64748b;
                font-size: 12px;
            }
            QLabel#fieldLabel {
                color: #334155;
                font-weight: 600;
            }
            QLabel#sectionTitle {
                color: #17202b;
                font-size: 14px;
                font-weight: 700;
            }
            QFrame#card {
                background: #ffffff;
                border: 1px solid #d8e0ea;
                border-radius: 8px;
                color: #17202b;
            }
            QLabel#cardTitle {
                color: #17202b;
                font-size: 13px;
                font-weight: 700;
            }
            QLineEdit, QComboBox {
                min-height: 34px;
                border: 1px solid #c7d0dd;
                border-radius: 6px;
                color: #101828;
                selection-background-color: #2f9e7e;
            }
            QLineEdit {
                padding: 4px 10px;
                background: #ffffff;
            }
            QComboBox {
                padding: 4px 28px 4px 10px;
                background: #f8fafc;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #229b76;
            }
            QLineEdit:focus {
                background: #ffffff;
            }
            QComboBox:focus, QComboBox:hover {
                background: #eef4fb;
                border-color: #94a3b8;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border: 0;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: url("__CHEVRON__");
                width: 12px;
                height: 12px;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #c7d0dd;
                selection-background-color: #dcefe8;
                selection-color: #101828;
                background: #ffffff;
                color: #101828;
                outline: 0;
            }
            QPushButton {
                min-height: 30px;
                border: 1px solid #c7d0dd;
                border-radius: 6px;
                padding: 3px 12px;
                background: #ffffff;
                color: #17202b;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #f1f5f9;
                border-color: #94a3b8;
            }
            QPushButton:disabled {
                color: #94a3b8;
                background: #eef2f7;
                border-color: #d8e0ea;
            }
            QPushButton#primaryButton {
                min-width: 150px;
                min-height: 40px;
                background: #1f9f78;
                color: #ffffff;
                border-color: #1f9f78;
            }
            QPushButton#primaryButton:hover {
                background: #188966;
                border-color: #188966;
            }
            QPushButton#secondaryButton {
                min-height: 34px;
                border-radius: 6px;
                padding: 4px 12px;
                background: #ffffff;
                border-color: #c7d0dd;
                color: #17202b;
                font-weight: 500;
            }
            QPushButton#secondaryButton:hover {
                background: #f1f5f9;
                border-color: #94a3b8;
            }
            QRadioButton, QCheckBox {
                color: #17202b;
                spacing: 8px;
                min-height: 25px;
            }
            QRadioButton::indicator, QCheckBox::indicator {
                width: 14px;
                height: 14px;
            }
            QRadioButton::indicator {
                border-radius: 7px;
                border: 1px solid #94a3b8;
                background: #ffffff;
            }
            QRadioButton::indicator:checked {
                border: 4px solid #1f9f78;
                background: #ffffff;
            }
            QCheckBox::indicator {
                border: 1px solid #94a3b8;
                border-radius: 3px;
                background: #ffffff;
            }
            QCheckBox::indicator:checked {
                background: #1f9f78;
                border-color: #1f9f78;
            }
            QProgressBar {
                border: 0;
                border-radius: 4px;
                background: #e2e8f0;
            }
            QProgressBar::chunk {
                border-radius: 4px;
                background: #1f9f78;
            }
            QFrame#separator {
                color: #d8e0ea;
                background: #d8e0ea;
                max-height: 1px;
            }
            QTextEdit#logView {
                border: 1px solid #d8e0ea;
                border-radius: 8px;
                background: #ffffff;
                color: #17202b;
                padding: 10px;
                font-family: "Cascadia Mono", Consolas, monospace;
                font-size: 12px;
            }
            """
        else:
            qss = """
            QWidget#page {
                background: #0b1117;
                color: #d8e1ea;
                font-family: "Segoe UI", "Microsoft YaHei UI", Arial, sans-serif;
                font-size: 13px;
            }
            QLabel#appTitle {
                color: #f4f7fb;
                font-size: 26px;
                font-weight: 700;
            }
            QLabel#statusText, QLabel#hintText {
                color: #8b9aae;
                font-size: 12px;
            }
            QLabel#fieldLabel {
                color: #aebbd0;
                font-weight: 600;
            }
            QLabel#sectionTitle {
                color: #e7edf5;
                font-size: 14px;
                font-weight: 700;
            }
            QFrame#card {
                background: #101820;
                border: 1px solid #233142;
                border-radius: 8px;
                color: #e7edf5;
            }
            QLabel#cardTitle {
                color: #e7edf5;
                font-size: 13px;
                font-weight: 700;
            }
            QLineEdit, QComboBox {
                min-height: 34px;
                border: 1px solid #2d3d50;
                border-radius: 6px;
                color: #ecf2f8;
                selection-background-color: #2f9e7e;
            }
            QLineEdit {
                padding: 4px 10px;
                background: #0d141d;
            }
            QComboBox {
                padding: 4px 28px 4px 10px;
                background: #101a25;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #3fbf95;
            }
            QLineEdit:focus {
                background: #101a25;
            }
            QComboBox:focus {
                background: #132030;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border: 0;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: url("__CHEVRON__");
                width: 12px;
                height: 12px;
                margin-right: 8px;
            }
            QComboBox:hover {
                background: #132030;
                border-color: #3b5068;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #334255;
                selection-background-color: #1f7a5f;
                selection-color: #ffffff;
                background: #101a25;
                color: #ecf2f8;
                outline: 0;
            }
            QPushButton {
                min-height: 30px;
                border: 1px solid #2d3d50;
                border-radius: 6px;
                padding: 3px 12px;
                background: #111c2a;
                color: #e7edf5;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #162235;
                border-color: #3b5068;
            }
            QPushButton:disabled {
                color: #6d7b8f;
                background: #111a24;
                border-color: #263343;
            }
            QPushButton#primaryButton {
                min-width: 150px;
                min-height: 40px;
                background: #1f9f78;
                color: #ffffff;
                border-color: #1f9f78;
            }
            QPushButton#primaryButton:hover {
                background: #24b487;
                border-color: #24b487;
            }
            QPushButton#secondaryButton {
                min-height: 34px;
                border-radius: 6px;
                padding: 4px 12px;
                background: #0d141d;
                border-color: #2a394b;
                color: #e0e8f2;
                font-weight: 500;
            }
            QPushButton#secondaryButton:hover {
                background: #152131;
                border-color: #3a4c61;
            }
            QRadioButton, QCheckBox {
                color: #d8e1ea;
                spacing: 8px;
                min-height: 25px;
            }
            QRadioButton::indicator, QCheckBox::indicator {
                width: 14px;
                height: 14px;
            }
            QRadioButton::indicator {
                border-radius: 7px;
                border: 1px solid #56677d;
                background: #0d141d;
            }
            QRadioButton::indicator:checked {
                border: 4px solid #24b487;
                background: #ffffff;
            }
            QCheckBox::indicator {
                border: 1px solid #56677d;
                border-radius: 3px;
                background: #0d141d;
            }
            QCheckBox::indicator:checked {
                background: #24b487;
                border-color: #24b487;
            }
            QProgressBar {
                border: 0;
                border-radius: 4px;
                background: #1a2635;
            }
            QProgressBar::chunk {
                border-radius: 4px;
                background: #24b487;
            }
            QFrame#separator {
                color: #263343;
                background: #263343;
                max-height: 1px;
            }
            QTextEdit#logView {
                border: 1px solid #233142;
                border-radius: 8px;
                background: #0d141d;
                color: #d8e1ea;
                padding: 10px;
                font-family: "Cascadia Mono", Consolas, monospace;
                font-size: 12px;
            }
            """
        self.setStyleSheet(qss.replace("__CHEVRON__", chevron))

    def _retranslate_ui(self):
        self.setWindowTitle(self._tr("title"))
        self._status_label.setText(self._tr("ready"))
        self._theme_label.setText(self._tr("theme"))
        current_theme = self._theme
        self._theme_combo.blockSignals(True)
        self._theme_combo.clear()
        self._theme_combo.addItem(self._tr("theme_dark"), "dark")
        self._theme_combo.addItem(self._tr("theme_light"), "light")
        index = self._theme_combo.findData(current_theme)
        self._theme_combo.setCurrentIndex(max(index, 0))
        self._theme_combo.blockSignals(False)
        self._lang_label.setText(self._tr("language"))
        self._sdk_title.setText(self._tr("sdk_root"))
        self._sdk_tip.setText(self._tr("sdk_root_tip"))
        self._root_label.setText(self._tr("root_path"))
        self._root_btn.setText(self._tr("browse"))
        self._proj_title.setText(self._tr("project_settings"))
        self._family_label.setText(self._tr("chip_family"))
        self._chip_label.setText(self._tr("chip_model"))
        self._name_label.setText(self._tr("project_name"))
        self._out_label.setText(self._tr("output_dir"))
        self._out_btn.setText(self._tr("browse"))
        self._tmpl_title.setText(self._tr("code_template"))
        self._tmpl_empty.setText(self._tr("tmpl_empty"))
        self._tmpl_led.setText(self._tr("tmpl_led"))
        self._tmpl_uart.setText(self._tr("tmpl_uart"))
        self._gen_btn.setText(self._tr("generate"))
        self._log_title.setText(self._tr("log"))
        self._clear_log_btn.setText(self._tr("clear_log"))
        self._lib_title.setText(self._tr("optional_libs"))
        self._lib_freertos.setText(self._tr("lib_freertos"))
        self._lib_rtt_nano.setText(self._tr("lib_rtt_nano"))
        self._lib_gcc.setText(self._tr("lib_gcc"))
        self._about_btn.setText(self._tr("about"))
        self._help_btn.setText(self._tr("help"))
        self._hxtal_label.setText(self._tr("hxtal_freq"))

    def _show_help(self):
        QMessageBox.information(self, self._tr("help"), self._tr("help_text"))

    def _show_about(self):
        QMessageBox.about(self, self._tr("about_title"), self._tr("about_text"))

    def _on_lang_changed(self, text: str):
        lang = "zh" if text == "Chinese" else "en"
        self._i18n.set_language(lang)
        self._retranslate_ui()

    def _on_theme_changed(self):
        theme = self._theme_combo.currentData()
        if theme:
            self._theme = theme
            self._apply_theme()

    def _browse_sdk(self):
        path = QFileDialog.getExistingDirectory(self, self._tr("select_sdk_root"))
        if path:
            self._sdk_root.setText(path)
            self._sdk.set_path("SDK_ROOT", path)

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(self, self._tr("select_output"))
        if path:
            self._output_dir.setText(path)

    def _populate_families(self):
        self._family_combo.addItems(self._chip_db.get_families())

    def _on_family_changed(self, family: str):
        self._chip_combo.clear()
        self._chip_combo.addItems(self._chip_db.get_chips_for_family(family))

    def _on_rtos_toggled(self, checked: bool):
        sender = self.sender()
        if checked:
            if sender is self._lib_freertos:
                self._lib_rtt_nano.setChecked(False)
            elif sender is self._lib_rtt_nano:
                self._lib_freertos.setChecked(False)

    def _clear_log(self):
        self._log.clear()

    def _log_msg(self, msg: str, level: str = "info"):
        if self._theme == "light":
            colors = {
                "info": ("INFO", "#0369a1"),
                "success": ("DONE", "#15803d"),
                "error": ("ERROR", "#b91c1c"),
                "warn": ("WARN", "#a16207"),
            }
            time_color = "#64748b"
            text_color = "#17202b"
        else:
            colors = {
                "info": ("INFO", "#7dd3fc"),
                "success": ("DONE", "#86efac"),
                "error": ("ERROR", "#fca5a5"),
                "warn": ("WARN", "#fcd34d"),
            }
            time_color = "#667085"
            text_color = "#d0d5dd"
        badge, badge_color = colors.get(level, colors["info"])
        text = html.escape(msg)
        keywords = {
            "SDK": "#fcd34d",
            "Keil": "#c4b5fd",
            "GCC": "#93c5fd",
            "CMake": "#93c5fd",
            "FreeRTOS": "#86efac",
            "RT-Thread": "#f0abfc",
            "Error": "#fca5a5",
            "Done": "#86efac",
            "Generating": "#7dd3fc",
            "错误": "#fca5a5",
            "完成": "#86efac",
            "正在生成": "#7dd3fc",
            "工程": "#fcd34d",
        }
        for word, color in keywords.items():
            text = text.replace(
                html.escape(word),
                f"<span style='color:{color}; font-weight:700;'>{html.escape(word)}</span>",
            )
        now = datetime.now().strftime("%H:%M:%S")
        self._log.append(
            "<div style='white-space:pre-wrap;'>"
            f"<span style='color:{time_color};'>{now}</span> "
            f"<span style='color:{badge_color}; font-weight:700;'>[{badge}]</span> "
            f"<span style='color:{text_color};'>{text}</span>"
            "</div>"
        )

    def _set_busy(self, busy: bool, idle_text: str | None = None):
        self._gen_btn.setEnabled(not busy)
        self._progress.setVisible(busy)
        self._status_label.setText(self._tr("generating_btn") if busy else (idle_text or self._tr("ready")))
        self._gen_btn.setText(self._tr("generating_btn") if busy else self._tr("generate"))

    def _on_generate(self):
        sdk_root = self._sdk_root.text().strip()
        family = self._family_combo.currentText()
        chip = self._chip_combo.currentText()
        proj_name = self._proj_name.text().strip()
        output_dir = Path(self._output_dir.text().strip())

        if sdk_root and sdk_root != self._sdk.get_path("SDK_ROOT"):
            self._sdk.set_path("SDK_ROOT", sdk_root)

        if not family or not chip:
            QMessageBox.warning(self, self._tr("error"), self._tr("err_select_chip"))
            return
        if not proj_name:
            QMessageBox.warning(self, self._tr("error"), self._tr("err_project_name"))
            return
        if not self._sdk.get_path("SDK_ROOT"):
            QMessageBox.warning(self, self._tr("error"), self._tr("err_sdk_root"))
            return

        chip_config = self._chip_db.get_chip(family, chip)
        if not chip_config:
            QMessageBox.warning(
                self,
                self._tr("error"),
                self._tr("err_chip_not_found", chip=chip),
            )
            return

        hxtal_mhz = int(self._hxtal_combo.currentText().split()[0])
        chip_config = dict(chip_config)
        chip_config["config"] = dict(chip_config.get("config", {}))
        chip_config["config"]["hxtal_hz"] = hxtal_mhz * 1000000

        tmpl_type = "empty"
        if self._tmpl_led.isChecked():
            tmpl_type = "led"
        elif self._tmpl_uart.isChecked():
            tmpl_type = "uart"

        optional_libs = []
        if self._lib_freertos.isChecked():
            optional_libs.append("freertos")
        if self._lib_rtt_nano.isChecked():
            optional_libs.append("rtt_nano")

        build_system = "both" if self._lib_gcc.isChecked() else "keil"

        self._set_busy(True)
        QApplication.processEvents()

        try:
            output_path = output_dir / proj_name
            self._log_msg(
                self._tr("generating", proj_name=proj_name, chip=chip, tmpl_type=tmpl_type),
                "info",
            )
            self._gen.generate(
                family,
                chip,
                chip_config,
                proj_name,
                output_path,
                tmpl_type,
                optional_libs=optional_libs,
                build_system=build_system,
            )
            self._set_busy(False, self._tr("done_status"))
            self._log_msg(self._tr("done", path=str(output_path)), "success")
            issue_count = self._log_validation_report(
                output_path,
                proj_name,
                chip_config,
                optional_libs,
                build_system,
            )
            if issue_count:
                self._status_label.setText(self._tr("report_issues", count=issue_count))
            else:
                self._status_label.setText(self._tr("report_ok"))
        except Exception as exc:
            self._log_msg(f"Error: {exc}", "error")
            QMessageBox.critical(self, self._tr("error"), str(exc))
        finally:
            if self._progress.isVisible():
                self._set_busy(False)

    def _log_validation_report(
        self,
        output_path: Path,
        project_name: str,
        chip_config: dict,
        optional_libs: list[str],
        build_system: str,
    ) -> int:
        results = self._validator.validate(
            output_path,
            project_name,
            chip_config,
            optional_libs=optional_libs,
            build_system=build_system,
        )
        issue_count = sum(1 for item in results if item.status != "ok")
        ok_count = len(results) - issue_count
        summary_level = "warn" if issue_count else "success"
        self._log_msg(
            f"Generation report: {ok_count} passed, {issue_count} issue(s)",
            summary_level,
        )
        for item in results:
            if item.status == "ok":
                level = "success"
                badge = "OK"
            elif item.status == "warn":
                level = "warn"
                badge = "WARN"
            else:
                level = "error"
                badge = "ERROR"
            detail = f" - {item.detail}" if item.detail else ""
            self._log_msg(f"[CHECK] {badge} {item.name}{detail}", level)
        return issue_count
