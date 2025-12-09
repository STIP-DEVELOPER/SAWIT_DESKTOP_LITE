import cv2
import numpy as np
import pyrealsense2 as rs
from ultralytics import YOLO

# -------------------------------
#  1. Load YOLO11 NCNN Model
# -------------------------------
model = YOLO("yolo11n_ncnn_model")

# -------------------------------
#  2. Initialize Intel RealSense
# -------------------------------
pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

profile = pipeline.start(config)

# Align depth to color frame
align_to = rs.stream.color
align = rs.align(align_to)

# Depth scale (convert raw depth → meter)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()  # usually 0.001 meters


# -------------------------------
#  3. Loop: Capture + Detect + Distance
# -------------------------------
while True:
    # Get frames
    frames = pipeline.wait_for_frames()
    aligned_frames = align.process(frames)
    
    color_frame = aligned_frames.get_color_frame()
    depth_frame = aligned_frames.get_depth_frame()

    if not color_frame or not depth_frame:
        continue

    color_image = np.asanyarray(color_frame.get_data())
    depth_image = np.asanyarray(depth_frame.get_data())

    # --------------------------------------
    # Run YOLO11 (NCNN backend)
    # --------------------------------------
    results = model(color_image)

    # Draw detections
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].astype(int)
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            # --------------------------------------
            # Measure depth at the center of bounding box
            # --------------------------------------
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            # Get depth (RAW units → meters)
            depth_raw = depth_image[cy, cx]
            distance = depth_raw * depth_scale  # convert to meters

            # Safety check
            if distance == 0 or distance > 10:
                distance_text = "No Depth"
            else:
                distance_text = f"{distance:.2f} m"

            # Draw bbox
            cv2.rectangle(color_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label
            cv2.putText(
                color_image,
                f"{label} {conf:.2f} {distance_text}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            # Draw center point
            cv2.circle(color_image, (cx, cy), 4, (0, 0, 255), -1)

    # Show visualization
    cv2.imshow("YOLO11 + Depth", color_image)

    if cv2.waitKey(1) == ord('q'):
        break

# Stop pipeline
pipeline.stop()
cv2.destroyAllWindows()
