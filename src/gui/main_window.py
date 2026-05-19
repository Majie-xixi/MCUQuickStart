"""Main window for MCU Template Generator."""
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QTextEdit, QGroupBox, QRadioButton, QFileDialog, QMessageBox,
)
from PyQt6.QtCore import Qt
from src.core.chip_db import ChipDatabase
from src.core.sdk_manager import SDKManager
from src.core.project_generator import ProjectGenerator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCU Template Generator")
        self.setMinimumSize(650, 550)

        self._sdk = SDKManager()
        self._sdk.load_config()
        self._chip_db = ChipDatabase(Path(__file__).parent.parent / "resources" / "chips")
        self._chip_db.load()
        self._gen = ProjectGenerator(
            Path(__file__).parent.parent / "resources" / "templates",
            self._sdk,
        )

        self._build_ui()
        self._populate_families()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # --- SDK Config ---
        sdk_group = QGroupBox("SDK Root")
        sdk_layout = QVBoxLayout(sdk_group)
        tip = QLabel("All chip SDK packages should be placed under this directory.")
        tip.setStyleSheet("color: gray; font-size: 11px;")
        sdk_layout.addWidget(tip)

        root_row = QHBoxLayout()
        root_row.addWidget(QLabel("Root Path:"))
        self._sdk_root = QLineEdit(self._sdk.get_path("SDK_ROOT"))
        root_row.addWidget(self._sdk_root)
        root_btn = QPushButton("Browse...")
        root_btn.clicked.connect(lambda: self._browse_sdk("SDK_ROOT", self._sdk_root))
        root_row.addWidget(root_btn)
        sdk_layout.addLayout(root_row)

        layout.addWidget(sdk_group)

        # --- Project Settings ---
        proj_group = QGroupBox("Project Settings")
        proj_layout = QVBoxLayout(proj_group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Chip Family:"))
        self._family_combo = QComboBox()
        self._family_combo.currentTextChanged.connect(self._on_family_changed)
        row1.addWidget(self._family_combo)
        row1.addWidget(QLabel("Chip Model:"))
        self._chip_combo = QComboBox()
        row1.addWidget(self._chip_combo)
        proj_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Project Name:"))
        self._proj_name = QLineEdit("MyProject")
        row2.addWidget(self._proj_name)
        proj_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Output Dir:"))
        self._output_dir = QLineEdit(str(Path.home() / "Desktop"))
        row3.addWidget(self._output_dir)
        out_btn = QPushButton("Browse...")
        out_btn.clicked.connect(self._browse_output)
        row3.addWidget(out_btn)
        proj_layout.addLayout(row3)

        layout.addWidget(proj_group)

        # --- Template Choice ---
        tmpl_group = QGroupBox("Code Template")
        tmpl_layout = QVBoxLayout(tmpl_group)
        self._tmpl_empty = QRadioButton("Empty (main loop only)")
        self._tmpl_empty.setChecked(True)
        self._tmpl_led = QRadioButton("LED Blink")
        self._tmpl_uart = QRadioButton("UART Printf")
        tmpl_layout.addWidget(self._tmpl_empty)
        tmpl_layout.addWidget(self._tmpl_led)
        tmpl_layout.addWidget(self._tmpl_uart)
        layout.addWidget(tmpl_group)

        # --- Generate Button ---
        gen_btn = QPushButton("Generate Project")
        gen_btn.setMinimumHeight(36)
        gen_btn.clicked.connect(self._on_generate)
        layout.addWidget(gen_btn)

        # --- Log Output ---
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        log_layout.addWidget(self._log)
        layout.addWidget(log_group)

    def _browse_sdk(self, vendor: str, line_edit: QLineEdit):
        path = QFileDialog.getExistingDirectory(self, f"Select {vendor} SDK Root")
        if path:
            line_edit.setText(path)
            self._sdk.set_path(vendor, path)

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self._output_dir.setText(path)

    def _populate_families(self):
        families = self._chip_db.get_families()
        self._family_combo.addItems(families)

    def _on_family_changed(self, family: str):
        self._chip_combo.clear()
        chips = self._chip_db.get_chips_for_family(family)
        self._chip_combo.addItems(chips)

    def _log_msg(self, msg: str):
        self._log.append(msg)

    def _on_generate(self):
        family = self._family_combo.currentText()
        chip = self._chip_combo.currentText()
        proj_name = self._proj_name.text().strip()
        output_dir = Path(self._output_dir.text().strip())

        if not family or not chip:
            QMessageBox.warning(self, "Error", "Please select a chip.")
            return
        if not proj_name:
            QMessageBox.warning(self, "Error", "Please enter a project name.")
            return
        if not self._sdk.get_path("SDK_ROOT"):
            QMessageBox.warning(self, "Error", "Please set the SDK root directory.")
            return

        chip_config = self._chip_db.get_chip(family, chip)
        if not chip_config:
            QMessageBox.warning(self, "Error", f"Chip {chip} not found in database.")
            return

        tmpl_type = "empty"
        if self._tmpl_led.isChecked():
            tmpl_type = "led"
        elif self._tmpl_uart.isChecked():
            tmpl_type = "uart"

        try:
            output_path = output_dir / proj_name
            self._log_msg(f"Generating {proj_name} for {chip} ({tmpl_type})...")
            self._gen.generate(family, chip, chip_config, proj_name, output_path, tmpl_type)
            self._log_msg("Done! Project created at: " + str(output_path))
            QMessageBox.information(self, "Success", f"Project generated at:\n{output_path}")
        except Exception as e:
            self._log_msg(f"Error: {e}")
            QMessageBox.critical(self, "Error", str(e))
