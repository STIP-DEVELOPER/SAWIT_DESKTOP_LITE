import os

# Force Qt to use system plugin
# os.environ.pop("QT_PLUGIN_PATH", None)
# os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = (
#     "/usr/lib/arm-linux-gnueabihf/qt5/plugins/platforms"
# )
# os.environ["QT_QPA_PLATFORM"] = "xcb"

import os

os.environ["QT_STYLE_OVERRIDE"] = "Fusion"


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
