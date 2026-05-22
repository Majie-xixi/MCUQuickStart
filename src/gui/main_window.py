"""Main window for MCU Template Generator."""
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QTextEdit, QGroupBox, QRadioButton, QFileDialog, QMessageBox,
    QCheckBox,
)
from PyQt6.QtCore import Qt
from src.core.chip_db import ChipDatabase
from src.core.sdk_manager import SDKManager
from src.core.project_generator import ProjectGenerator
from src.core.i18n import I18n


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(680, 580)
        self.setStyleSheet("""
            QMainWindow { background: #f0f2f5; }
            QGroupBox {
                background: #ffffff; border: 1px solid #e0e4e8;
                border-radius: 8px; margin-top: 8px; padding-top: 14px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; }
            QPushButton { border: 1px solid #d0d5dd; border-radius: 5px; padding: 5px 14px; background: #fafbfc; }
            QPushButton:hover { background: #e8ecf0; }
            QLineEdit { border: 1px solid #d0d5dd; border-radius: 4px; padding: 3px 6px; background: white; }
            QComboBox { border: 1px solid #d0d5dd; border-radius: 4px; padding: 3px 8px; }
            QComboBox QAbstractItemView { selection-background-color: #e0e8f0; }
            QTextEdit { border-radius: 6px; font-family: "Consolas", monospace; }
        """)

        self._i18n = I18n(Path(__file__).parent.parent / "resources" / "i18n")
        self._i18n.set_language("en")

        self._sdk = SDKManager()
        self._sdk.load_config()
        self._chip_db = ChipDatabase(Path(__file__).parent.parent / "resources" / "chips")
        self._chip_db.load()
        self._gen = ProjectGenerator(
            Path(__file__).parent.parent / "resources" / "templates",
            self._sdk,
        )

        self._build_ui()
        self._retranslate_ui()
        self._populate_families()

    # ── i18n helper ──────────────────────────────────────────────
    def _tr(self, key: str, **kwargs) -> str:
        return self._i18n.get(key, **kwargs)

    # ── UI construction ──────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # --- Top bar: help button + language selector ---
        top = QHBoxLayout()
        self._help_btn = QPushButton()
        self._help_btn.setFixedWidth(80)
        self._help_btn.clicked.connect(self._show_help)
        top.addWidget(self._help_btn)
        top.addStretch()
        top.addWidget(QLabel(""))
        self._lang_label = top.itemAt(top.count() - 1).widget()
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(["中文", "English"])
        self._lang_combo.setCurrentText("English")
        self._lang_combo.currentTextChanged.connect(self._on_lang_changed)
        top.addWidget(self._lang_combo)
        layout.addLayout(top)

        # --- SDK Config ---
        self._sdk_group = QGroupBox()
        sdk_layout = QVBoxLayout(self._sdk_group)
        self._sdk_tip = QLabel()
        self._sdk_tip.setStyleSheet("color: gray; font-size: 11px;")
        sdk_layout.addWidget(self._sdk_tip)

        root_row = QHBoxLayout()
        self._root_label = QLabel()
        root_row.addWidget(self._root_label)
        self._sdk_root = QLineEdit(self._sdk.get_path("SDK_ROOT"))
        root_row.addWidget(self._sdk_root)
        self._root_btn = QPushButton()
        self._root_btn.clicked.connect(lambda: self._browse_sdk())
        root_row.addWidget(self._root_btn)
        sdk_layout.addLayout(root_row)

        layout.addWidget(self._sdk_group)

        # --- Project Settings ---
        self._proj_group = QGroupBox()
        proj_layout = QVBoxLayout(self._proj_group)

        row1 = QHBoxLayout()
        self._family_label = QLabel()
        row1.addWidget(self._family_label)
        self._family_combo = QComboBox()
        self._family_combo.currentTextChanged.connect(self._on_family_changed)
        row1.addWidget(self._family_combo)
        self._chip_label = QLabel()
        row1.addWidget(self._chip_label)
        self._chip_combo = QComboBox()
        row1.addWidget(self._chip_combo)
        proj_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self._name_label = QLabel()
        row2.addWidget(self._name_label)
        self._proj_name = QLineEdit("MyProject")
        row2.addWidget(self._proj_name)
        proj_layout.addLayout(row2)

        row3 = QHBoxLayout()
        self._out_label = QLabel()
        row3.addWidget(self._out_label)
        self._output_dir = QLineEdit(str(Path.home() / "Desktop"))
        row3.addWidget(self._output_dir)
        self._out_btn = QPushButton()
        self._out_btn.clicked.connect(self._browse_output)
        row3.addWidget(self._out_btn)
        proj_layout.addLayout(row3)

        row4 = QHBoxLayout()
        self._hxtal_label = QLabel()
        row4.addWidget(self._hxtal_label)
        self._hxtal_combo = QComboBox()
        self._hxtal_combo.addItems(["8 MHz", "25 MHz"])
        self._hxtal_combo.setCurrentText("8 MHz")
        row4.addWidget(self._hxtal_combo)
        row4.addStretch()
        proj_layout.addLayout(row4)

        layout.addWidget(self._proj_group)

        # --- Template Choice ---
        self._tmpl_group = QGroupBox()
        tmpl_layout = QVBoxLayout(self._tmpl_group)
        self._tmpl_empty = QRadioButton()
        self._tmpl_empty.setChecked(True)
        self._tmpl_led = QRadioButton()
        self._tmpl_uart = QRadioButton()
        tmpl_layout.addWidget(self._tmpl_empty)
        tmpl_layout.addWidget(self._tmpl_led)
        tmpl_layout.addWidget(self._tmpl_uart)
        layout.addWidget(self._tmpl_group)

        # --- Optional Libraries ---
        self._lib_group = QGroupBox()
        lib_layout = QVBoxLayout(self._lib_group)
        self._lib_freertos = QCheckBox()
        lib_layout.addWidget(self._lib_freertos)
        self._lib_gcc = QCheckBox()
        lib_layout.addWidget(self._lib_gcc)
        layout.addWidget(self._lib_group)

        # --- Generate Button ---
        self._gen_btn = QPushButton()
        self._gen_btn.setMinimumHeight(36)
        self._gen_btn.clicked.connect(self._on_generate)
        layout.addWidget(self._gen_btn)

        # --- Log Output ---
        self._log_group = QGroupBox()
        log_layout = QVBoxLayout(self._log_group)
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        log_layout.addWidget(self._log)
        layout.addWidget(self._log_group)

    # ── Retranslate all UI text ──────────────────────────────────
    def _retranslate_ui(self):
        self.setWindowTitle(self._tr("title"))
        self._lang_label.setText(self._tr("language"))
        self._sdk_group.setTitle(self._tr("sdk_root"))
        self._sdk_tip.setText(self._tr("sdk_root_tip"))
        self._root_label.setText(self._tr("root_path"))
        self._root_btn.setText(self._tr("browse"))
        self._proj_group.setTitle(self._tr("project_settings"))
        self._family_label.setText(self._tr("chip_family"))
        self._chip_label.setText(self._tr("chip_model"))
        self._name_label.setText(self._tr("project_name"))
        self._out_label.setText(self._tr("output_dir"))
        self._out_btn.setText(self._tr("browse"))
        self._tmpl_group.setTitle(self._tr("code_template"))
        self._tmpl_empty.setText(self._tr("tmpl_empty"))
        self._tmpl_led.setText(self._tr("tmpl_led"))
        self._tmpl_uart.setText(self._tr("tmpl_uart"))
        self._gen_btn.setText(self._tr("generate"))
        self._log_group.setTitle(self._tr("log"))
        self._lib_group.setTitle(self._tr("optional_libs"))
        self._lib_freertos.setText(self._tr("lib_freertos"))
        self._lib_gcc.setText(self._tr("lib_gcc"))
        self._help_btn.setText(self._tr("help"))
        self._hxtal_label.setText(self._tr("hxtal_freq"))

    # ── Help ─────────────────────────────────────────────────────
    def _show_help(self):
        QMessageBox.information(self, self._tr("help"), self._tr("help_text"))

    # ── Language switch ──────────────────────────────────────────
    def _on_lang_changed(self, text: str):
        lang = "zh" if text == "中文" else "en"
        self._i18n.set_language(lang)
        self._retranslate_ui()

    # ── SDK & output browsing ────────────────────────────────────
    def _browse_sdk(self):
        title = self._tr("select_sdk_root")
        path = QFileDialog.getExistingDirectory(self, title)
        if path:
            self._sdk_root.setText(path)
            self._sdk.set_path("SDK_ROOT", path)

    def _browse_output(self):
        title = self._tr("select_output")
        path = QFileDialog.getExistingDirectory(self, title)
        if path:
            self._output_dir.setText(path)

    # ── Chip selection ───────────────────────────────────────────
    def _populate_families(self):
        families = self._chip_db.get_families()
        self._family_combo.addItems(families)

    def _on_family_changed(self, family: str):
        self._chip_combo.clear()
        chips = self._chip_db.get_chips_for_family(family)
        self._chip_combo.addItems(chips)

    # ── Generate ─────────────────────────────────────────────────
    def _log_msg(self, msg: str):
        self._log.append(msg)

    def _on_generate(self):
        family = self._family_combo.currentText()
        chip = self._chip_combo.currentText()
        proj_name = self._proj_name.text().strip()
        output_dir = Path(self._output_dir.text().strip())

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
            QMessageBox.warning(self, self._tr("error"),
                                self._tr("err_chip_not_found", chip=chip))
            return

        hxtal_text = self._hxtal_combo.currentText()
        hxtal_mhz = int(hxtal_text.split()[0])
        chip_config = dict(chip_config)  # shallow copy to avoid mutating cache
        if "config" not in chip_config:
            chip_config["config"] = {}
        chip_config["config"] = dict(chip_config["config"])
        chip_config["config"]["hxtal_hz"] = hxtal_mhz * 1000000

        tmpl_type = "empty"
        if self._tmpl_led.isChecked():
            tmpl_type = "led"
        elif self._tmpl_uart.isChecked():
            tmpl_type = "uart"

        optional_libs = []
        if self._lib_freertos.isChecked():
            optional_libs.append("freertos")

        build_system = "both" if self._lib_gcc.isChecked() else "keil"

        try:
            output_path = output_dir / proj_name
            self._log_msg(self._tr("generating", proj_name=proj_name, chip=chip, tmpl_type=tmpl_type))
            self._gen.generate(family, chip, chip_config, proj_name, output_path, tmpl_type,
                               optional_libs=optional_libs, build_system=build_system)
            self._log_msg(self._tr("done", path=str(output_path)))
            QMessageBox.information(self, self._tr("success"),
                                    f"{output_path}")
        except Exception as e:
            self._log_msg(f"Error: {e}")
            QMessageBox.critical(self, self._tr("error"), str(e))
