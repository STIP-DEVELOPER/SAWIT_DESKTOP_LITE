import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap


def convert_frame_to_qpixmap(frame):
    """Konversi OpenCV BGR frame ke QPixmap."""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    bytes_per_line = ch * w
    qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg)


def draw_boxes_on_frame(frame, boxes, labels, confs):
    """Gambar bounding box pada frame hasil YOLO."""
    for box, label, conf in zip(boxes, labels, confs):
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"{label} {conf:.2f}",
            (x1, y1 - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
        )
    return frame
