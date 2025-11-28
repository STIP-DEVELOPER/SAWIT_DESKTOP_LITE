import os
import zipfile
import gdown
import shutil


class GoogleDriveUpgrader:
    def __init__(
        self, folder_id: str, target_dir: str = "models", temp_dir: str = "temp_upgrade"
    ):
        self.folder_id = folder_id
        self.target_dir = target_dir
        self.temp_dir = temp_dir

        self._ensure_folder(self.target_dir)

    def _ensure_folder(self, path: str):
        if not os.path.exists(path):
            os.makedirs(path)

    def download_folder(self):
        url = f"https://drive.google.com/drive/folders/{self.folder_id}"
        gdown.download_folder(url=url, output=self.temp_dir, use_cookies=False)

    def move_files(self):
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                shutil.move(
                    os.path.join(root, file), os.path.join(self.target_dir, file)
                )

    def extract_zip_files(self):
        for file in os.listdir(self.target_dir):
            file_path = os.path.join(self.target_dir, file)
            if zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(self.target_dir)
                os.remove(file_path)

    def cleanup(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run(self):
        self.download_folder()
        self.move_files()
        self.extract_zip_files()
        self.cleanup()
