import json
import os


class ConfigManager:
    def __init__(self, file_path="./src/configs/config.json", autosave=True):
        self.file_path = file_path
        self.autosave = autosave
        self.config = {}

        self._load()

    def _load(self):
        """Load configuration dari file JSON. Jika file tidak ada, buat default."""
        if not os.path.exists(self.file_path):
            self._save()  # buat file kosong
        else:
            try:
                with open(self.file_path, "r") as f:
                    self.config = json.load(f)
            except json.JSONDecodeError:
                # Jika file rusak/tidak valid, reset
                self.config = {}
                self._save()

    def _save(self):
        """Save configuration ke file JSON."""
        with open(self.file_path, "w") as f:
            json.dump(self.config, f, indent=4)

    def get_config(self, key, default=None):
        """Ambil nilai config berdasarkan key"""
        return self.config.get(key, default)

    def set_config(self, key, value):
        """Set nilai config dan auto-save jika diaktifkan."""
        self.config[key] = value
        if self.autosave:
            self._save()

    def remove_config(self, key):
        """Hapus key dari config."""
        if key in self.config:
            del self.config[key]
            if self.autosave:
                self._save()

    def get_all(self):
        """Ambil semua config (dictionary)."""
        return self.config
