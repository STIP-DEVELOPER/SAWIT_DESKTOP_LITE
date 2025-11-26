from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QTextEdit,
    QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie

from ui.input import InputForm
from ui.button import Button
from controller.upgrade import UpgradeThread
from configs import colors


class UpgradePage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Model Upgrade Tool")
        self.setStyleSheet(f"background-color: {colors.BACKGROUND_COLOR};")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(20)

        # ------------------------------------
        # CARD CONTAINER
        # ------------------------------------
        card = QFrame()
        card.setStyleSheet(
            f"""
            background-color: {colors.SURFACE_COLOR};
            border: 1px solid {colors.BORDER_COLOR};
            border-radius: 10px;
            """
        )
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(18)

        # ------------------------------------
        # TITLE
        # ------------------------------------
        title = QLabel("Upgrade Models & Sample Videos")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {colors.TEXT_PRIMARY};"
        )
        card_layout.addWidget(title)

        # ------------------------------------
        # FOLDER INPUT
        # ------------------------------------
        self.folder_input = InputForm(
            label="Google Drive Folder ID",
            placeholder="Enter Google Drive Folder ID",
            prefix_icon="assets/icons/folder.png",
            size="md",
        )
        card_layout.addWidget(self.folder_input)

        # ------------------------------------
        # BUTTONS (SIDE BY SIDE)
        # ------------------------------------
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_upgrade_models = Button(
            "Upgrade Models",
            icon_path="assets/icons/upload.png",
            bg_color=colors.PRIMARY_COLOR,
            hover_color=colors.PRIMARY_HOVER,
        )
        self.btn_upgrade_models.clicked.connect(self.upgrade_models)

        self.btn_upgrade_videos = Button(
            "Upgrade Sample Video",
            icon_path="assets/icons/video.png",
            bg_color=colors.ACCENT_COLOR,
            hover_color=colors.ACCENT_HOVER,
        )
        self.btn_upgrade_videos.clicked.connect(self.upgrade_sample_video)

        btn_row.addWidget(self.btn_upgrade_models)
        btn_row.addWidget(self.btn_upgrade_videos)

        card_layout.addLayout(btn_row)

        # ------------------------------------
        # LOADING SPINNER
        # ------------------------------------
        self.spinner = QMovie("assets/icons/spinner.gif")
        self.loading_label = QLabel("")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setMovie(self.spinner)
        self.loading_label.setVisible(False)
        card_layout.addWidget(self.loading_label)

        # ------------------------------------
        # LOG OUTPUT BOX
        # ------------------------------------
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet(
            f"""
            background-color: {colors.WHITE};
            border: 1px solid {colors.BORDER_COLOR};
            border-radius: 8px;
            padding: 8px;
            color: {colors.TEXT_PRIMARY};
            font-size: 13px;
            """
        )
        card_layout.addWidget(self.log_box)

        card.setLayout(card_layout)
        main_layout.addWidget(card)

        self.setLayout(main_layout)
        self.thread = None

    # -------------------------------------------------------
    # LOG
    # -------------------------------------------------------
    def append_log(self, message):
        self.log_box.append(message)

    # -------------------------------------------------------
    # LOADING UI
    # -------------------------------------------------------
    def set_loading(self, status: bool):
        if status:
            self.loading_label.setVisible(True)
            self.spinner.start()

            self.btn_upgrade_models.setDisabled(True)
            self.btn_upgrade_videos.setDisabled(True)
            self.folder_input.input.setDisabled(True)
        else:
            self.spinner.stop()
            self.loading_label.setVisible(False)

            self.btn_upgrade_models.setDisabled(False)
            self.btn_upgrade_videos.setDisabled(False)
            self.folder_input.input.setDisabled(False)

    # -------------------------------------------------------
    # PROCESS
    # -------------------------------------------------------
    def run_upgrade(self, folder_id, target_dir):
        self.set_loading(True)
        self.thread = UpgradeThread(folder_id, target_dir)
        self.thread.log_signal.connect(self.append_log)
        self.thread.finished.connect(self.on_upgrade_finished)
        self.thread.start()

    def on_upgrade_finished(self):
        self.set_loading(False)
        self.append_log("\n✔ Upgrade Completed!\n")

    # -------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------
    def upgrade_models(self):
        folder_id = (
            self.folder_input.get_value().strip() or "19usAPzpfeNHq4c9mxSAJZQ0M7g0AlNHo"
        )

        self.append_log(f"▶ Starting model upgrade (ID: {folder_id})...\n")
        self.run_upgrade(folder_id, "models")

    def upgrade_sample_video(self):
        folder_id = (
            self.folder_input.get_value().strip() or "1gokdUNV1NgoYOjzWjnkxMDrZ_9KCsa0c"
        )

        self.append_log(f"▶ Starting video upgrade (ID: {folder_id})...\n")
        self.run_upgrade(folder_id, "videos")
