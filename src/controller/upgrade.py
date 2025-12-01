from PyQt5.QtCore import QThread, pyqtSignal

from controller.gdrive import GoogleDriveUpgrader
from enums.log import LogLevel, LogSource
from utils.logger import add_log


class UpgradeThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, folder_id, target_dir):
        super().__init__()
        self.folder_id = folder_id
        self.target_dir = target_dir

    def log(self, msg):
        self.log_signal.emit(msg)

    def run(self):
        try:
            upgrader = GoogleDriveUpgrader(
                folder_id=self.folder_id, target_dir=self.target_dir
            )

            self.log("Downloading upgrade package...")
            upgrader.download_folder()

            self.log("Moving files...")
            upgrader.move_files()

            self.log("Extracting ZIP...")
            upgrader.extract_zip_files()

            self.log("Cleaning up temp...")
            upgrader.cleanup()

            add_log(
                LogLevel.INFO.value,
                LogSource.UI_UPGRADER.value,
                f"Upgrade completed successfully",
            )

        except Exception as e:
            add_log(
                LogLevel.ERROR.value,
                LogSource.UI_UPGRADER.value,
                f"Upgrade error: {str(e)}",
            )
            self.log(f"❌ ERROR: {str(e)}")
