import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.gui.main_window import MainWindow


def main():
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
