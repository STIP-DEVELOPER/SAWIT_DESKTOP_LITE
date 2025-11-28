from PyQt5.QtCore import QThread, pyqtSignal

from controller.gdrive import GoogleDriveUpgrader


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

        except Exception as e:
            self.log(f"❌ ERROR: {str(e)}")
