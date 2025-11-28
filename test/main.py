import time
import cv2
from ultralytics import YOLO

model = YOLO("yolo11n.pt")
cap = cv2.VideoCapture(0)

while True:
    t0 = time.time()
    ret, frame = cap.read()
    t_cap = time.time() - t0

    t1 = time.time()
    results = model(frame)
    t_inf = time.time() - t1

    t2 = time.time()
    cv2.imshow("demo", frame)
    cv2.waitKey(1)
    t_show = time.time() - t2

    print(f"capture={t_cap:.4f}s, inference={t_inf:.4f}s, imshow={t_show:.4f}s")
