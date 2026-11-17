import sys
from PySide6.QtWidgets import QApplication, QMessageBox
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

    try:
        window = MainWindow()
    except Exception as error:
        QMessageBox.critical(
            None,
            "Freeboard could not start",
            str(error),
        )
        sys.exit(1)

    window.show()
    sys.exit(application.exec())


if __name__ == "__main__":
    main()