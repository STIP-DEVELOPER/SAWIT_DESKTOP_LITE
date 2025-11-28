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
from utils.icon import get_icon


class UpgradePage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(20)

        card = QFrame()
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(18)

        self.folder_input = InputForm(
            placeholder="Enter token",
            prefix_icon=get_icon("folder.png"),
            size="xl",
        )
        card_layout.addWidget(self.folder_input)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        self.btn_upgrade_models = Button(
            "Upgrade Models",
            icon_path=get_icon("upgrade.png"),
            bg_color=colors.PRIMARY_COLOR,
            hover_color=colors.PRIMARY_HOVER,
        )
        self.btn_upgrade_models.clicked.connect(self.upgrade_models)
        btn_row.addWidget(self.btn_upgrade_models)

        card_layout.addLayout(btn_row)

        self.spinner = QMovie("spinner.gif")
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
            self.folder_input.input.setDisabled(True)
        else:
            self.spinner.stop()
            self.loading_label.setVisible(False)
            self.btn_upgrade_models.setDisabled(False)
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
