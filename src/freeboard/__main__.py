import sys
from PySide6.QtWidgets import QApplication
from .gui import MainWindow
from pathlib import Path
from PySide6.QtGui import QIcon
from .config import ICON_PATH


def main() -> None:
    application = QApplication(sys.argv)
    application.setApplicationName("Freeboard")
    application.setApplicationVersion("0.1.0")
    application.setOrganizationName("Freeboard")

    application.setWindowIcon(QIcon(str(ICON_PATH)))

    window = MainWindow()
    window.show()

    sys.exit(application.exec())


if __name__ == "__main__":
    main()