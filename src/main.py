import sys
from PyQt5.QtWidgets import QApplication

from views.main import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

    add_log(LogLevel.INFO.value, LogSource.MAIN.value, "Application started")


if __name__ == "__main__":
    main()
