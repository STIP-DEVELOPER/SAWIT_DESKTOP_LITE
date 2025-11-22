import os
import json
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QFileDialog,
    QHBoxLayout,
    QSizePolicy,
    QMessageBox,
)

from ui.button import Button
from utils.icon import get_icon
from utils.logger import get_logs


class LoggerPage(QWidget):

    def __init__(self):
        super().__init__()
        self.logs_data = get_logs()  # Ganti nama variabel untuk lebih jelas
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("📜 System Logs")
        title.setStyleSheet("color: #ccc; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.logs_text.setStyleSheet(self.log_text_style())
        layout.addWidget(self.logs_text)

        self.reload_button = Button(text="reload", icon_path=get_icon("reload.png"))
        self.export_button = Button(text="export", icon_path=get_icon("save.png"))

        self.reload_button.clicked.connect(self.load_logs)
        self.export_button.clicked.connect(self.export_logs)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.reload_button)
        button_layout.addWidget(self.export_button)
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 10, 10, 0)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_logs(self):
        """Memuat dan menampilkan logs"""
        self.logs_text.clear()
        self.logs_data = get_logs()  # Refresh data logs

        if not self.logs_data:
            self.logs_text.setPlainText("No log data found.")
            return

        formatted_logs = "\n".join(
            f"[{log['timestamp']}] [{log['level']}] [{log['source']}] {log['message']}"
            for log in self.logs_data
        )

        self.logs_text.setPlainText(formatted_logs)

    def export_logs(self):
        """Export logs ke file JSON"""
        if not self.logs_data:
            QMessageBox.warning(self, "Export Failed", "No logs data to export.")
            return

        try:
            # Default filename dengan timestamp
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"logs_export_{timestamp}.json"

            path, _ = QFileDialog.getSaveFileName(
                self, "Export Logs", default_filename, "JSON Files (*.json)"
            )

            if path:
                if not path.lower().endswith(".json"):
                    path += ".json"

                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.logs_data, f, indent=4, ensure_ascii=False)

                self.logs_text.append(
                    f"\n[EXPORT] Logs successfully exported to: {path}"
                )

                QMessageBox.information(
                    self, "Export Successful", f"Logs successfully exported to:\n{path}"
                )

        except Exception as e:
            error_msg = f"Failed to export logs: {str(e)}"
            self.logs_text.append(f"\n[ERROR] {error_msg}")
            QMessageBox.critical(self, "Export Failed", error_msg)

    def showEvent(self, event):
        """Override showEvent to load logs when the page is shown."""
        super().showEvent(event)
        self.load_logs()

    def log_text_style(self):
        return """
            QTextEdit {
                background-color: #111;
                color: #0f0;
                border: 1px solid #333;
                border-radius: 6px;
                font-family: Consolas, monospace;
                font-size: 13px;
                padding: 8px;
            }
            """
