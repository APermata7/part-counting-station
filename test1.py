import sys
import time
import cv2
import torch
import threading
import RPi.GPIO as GPIO

# ===============================
# Tambahkan path HX711
# ===============================
sys.path.append('./hx711py')

from hx711 import HX711

# ===============================
# Variable Global
# ===============================
weight = 0.0
running = True

# ===============================
# Setup HX711
# ===============================
hx = HX711(5, 6)

hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(420.001)

hx.reset()
hx.tare()

print("HX711 Ready")

# ===============================
# Thread Pembacaan HX711
# ===============================
def read_weight():

    global weight
    global running

    while running:

        try:
            val = hx.get_weight(3)

            # Filter noise kecil
            if abs(val) < 1:
                val = 0

            weight = val

            hx.power_down()
            hx.power_up()

            time.sleep(0.1)

        except:
            pass

# ===============================
# Load YOLOv5
# ===============================
model = torch.hub.load(
    './yolov5',
    'custom',
    path='best.pt',
    source='local'
)

print("YOLOv5 Ready")

# Optional optimasi
model.conf = 0.5
model.iou = 0.45
model.max_det = 5

# ===============================
# Kamera
# ===============================
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ===============================
# Jalankan Thread HX711
# ===============================
weight_thread = threading.Thread(target=read_weight)

weight_thread.daemon = True
weight_thread.start()

print("Weight Thread Started")

# ===============================
# Main Loop Kamera + YOLO
# ===============================
try:

    while True:

        ret, frame = cap.read()

        if not ret:
            print("Kamera tidak terdeteksi")
            break

        # ===========================
        # YOLO Detection
        # ===========================
        results = model(frame)

        detections = results.xyxy[0]

        object_count = len(detections)

        # ===========================
        # Bounding Box
        # ===========================
        for det in detections:

            x1, y1, x2, y2, conf, cls = det

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            confidence = float(conf)
            class_id = int(cls)

            label = model.names[class_id]

            # Perkecil box
            shrink_percent = 0.25

            width = x2 - x1
            height = y2 - y1

            shrink_x = int(width * shrink_percent / 2)
            shrink_y = int(height * shrink_percent / 2)

            x1_new = x1 + shrink_x
            y1_new = y1 + shrink_y
            x2_new = x2 - shrink_x
            y2_new = y2 - shrink_y

            text = f"{label} {confidence:.2f}"

            # Bounding box
            cv2.rectangle(
                frame,
                (x1_new, y1_new),
                (x2_new, y2_new),
                (0, 255, 0),
                2
            )

            # Label
            cv2.putText(
                frame,
                text,
                (x1_new, y1_new - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        # ===========================
        # Display Object Count
        # ===========================
        cv2.putText(
            frame,
            f'Jumlah Objek: {object_count}',
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

        # ===========================
        # Display Weight
        # ===========================
        cv2.putText(
            frame,
            f'Berat: {weight:.1f} g',
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0),
            2
        )

        # ===========================
        # Display Camera
        # ===========================
        cv2.imshow("YOLOv5 + HX711", frame)

        # Tombol keluar
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Program dihentikan")

finally:

    running = False

    cap.release()

    cv2.destroyAllWindows()

    GPIO.cleanup()

    print("Program selesai")