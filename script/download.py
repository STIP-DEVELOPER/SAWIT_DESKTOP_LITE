import os
import zipfile
import gdown
import shutil


class GoogleDriveDownloader:
    def __init__(
        self,
        folder_id: str,
        models_dir: str = "models",
        temp_dir: str = "temp_download",
    ):
        self.folder_id = folder_id
        self.models_dir = models_dir
        self.temp_dir = temp_dir

        self._ensure_folder(self.models_dir)

    def _ensure_folder(self, path: str):
        """Create folder if it does not exist"""
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created folder: {path}")

    def download_folder(self):
        """Download all files from a public Google Drive folder"""
        folder_url = f"https://drive.google.com/drive/folders/{self.folder_id}"
        print(f"Downloading folder from Google Drive ({self.folder_id})...")
        gdown.download_folder(
            url=folder_url, output=self.temp_dir, quiet=False, use_cookies=False
        )

    def move_files_to_models(self):
        """Move downloaded files to the models folder"""
        print(f"Moving downloaded files to {self.models_dir}...")
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                src_path = os.path.join(root, file)
                dst_path = os.path.join(self.models_dir, file)
                shutil.move(src_path, dst_path)

    def extract_zip_files(self):
        """Extract any ZIP files in the models folder"""
        for file in os.listdir(self.models_dir):
            file_path = os.path.join(self.models_dir, file)
            if zipfile.is_zipfile(file_path):
                print(f"Extracting {file}...")
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(self.models_dir)
                os.remove(file_path)

    def cleanup(self):
        """Remove temporary download folder"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run(self):
        """Run the complete download → move → extract → cleanup process"""
        self.download_folder()
        self.move_files_to_models()
        self.extract_zip_files()
        self.cleanup()
        print("Download and extraction completed!")


def download_models():
    FOLDER_ID = "19usAPzpfeNHq4c9mxSAJZQ0M7g0AlNHo"
    downloader = GoogleDriveDownloader(folder_id=FOLDER_ID, models_dir="models")
    downloader.run()


def download_sample_video():
    FOLDER_ID = "1KzujBiNkU-P-qVjAffCcuBgBxmB0a9Lq"
    downloader = GoogleDriveDownloader(folder_id=FOLDER_ID, models_dir="videos")
    downloader.run()


if __name__ == "__main__":
    download_models()
    download_sample_video()
