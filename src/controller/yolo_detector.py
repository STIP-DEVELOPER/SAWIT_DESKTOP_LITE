from ultralytics import YOLO
import cv2
import threading
import queue
import time


class YOLOWebcamDetectorController:
    def __init__(self, model_path, conf_threshold=0.5, camera_index=0):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.camera_index = camera_index
        self.cap = None

        self.frame_queue = queue.Queue(maxsize=1)
        self.running = False

    def setup_webcam(
        self, width=640, height=480, camera_index=None, inferance_type="webcam"
    ):
        """Initialize camera/video capture and start async frame grabbing"""
        cam_index = camera_index if camera_index is not None else self.camera_index
        self._setup_camera(cam_index, width, height, inferance_type)
        self.running = True
        threading.Thread(target=self._frame_grabber, daemon=True).start()

    def _setup_camera(self, cam_index, width, height, inferance_type):
        """Internal: setup cv2.VideoCapture"""
        source = (
            cam_index if inferance_type == "webcam" else "videos/sample-large-1.MOV"
        )
        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise Exception(f"Failed to open camera/video source: {source}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def _frame_grabber(self):
        """Grab frames asynchronously and always keep only the latest frame"""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            self._update_frame_queue(frame)
            time.sleep(0.001)

    def _update_frame_queue(self, frame):
        """Update frame queue with the latest frame"""
        if not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                pass
        self.frame_queue.put(frame)

    def get_latest_frame(self):
        """Return the latest frame or None if no frame is available"""
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None

    def get_center_coordinates(self, box):
        """Return center x, top y, bottom y coordinates of a bounding box"""
        x1, y1, x2, y2 = box.xyxy[0]
        center_x = (int(x1) + int(x2)) / 2
        return center_x, int(y1), int(y2)

    def get_position(self, center_x, frame_width):
        """Determine LEFT or RIGHT based on center_x"""
        return "LEFT" if center_x < frame_width / 2 else "RIGHT"

    def cleanup(self):
        """Stop frame grabbing and release camera"""
        self.running = False
        time.sleep(0.05)
        if self.cap:
            self.cap.release()
