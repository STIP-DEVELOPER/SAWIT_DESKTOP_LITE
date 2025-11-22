import os
from PyQt5.QtGui import QIcon


def get_icon(name: str) -> QIcon:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    icon_path = os.path.join(base_dir, "assets", "icons", name)

    if not os.path.exists(icon_path):
        print(f"[WARNING] Icon not found: {icon_path}")
        return QIcon()

    return QIcon(icon_path)
