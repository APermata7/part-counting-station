import torch
import cv2

# Load model dari folder YOLOv5 lokal
model = torch.hub.load(
    './yolov5',              # folder lokal YOLOv5
    'custom',
    path='best.pt',
    source='local'     # penting agar tidak download lagi
)

# Kamera default
cap = cv2.VideoCapture(0)

# Resolusi kamera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Kamera tidak terdeteksi")
        break

    # Deteksi objek
    results = model(frame)

    detections = results.xyxy[0]

    # Hitung jumlah objek
    object_count = len(detections)

    for det in detections:
        x1, y1, x2, y2, conf, cls = det

        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)

        confidence = float(conf)
        class_id = int(cls)

        label = model.names[class_id]

        # Perkecil bounding box
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

        cv2.rectangle(frame,
                      (x1_new, y1_new),
                      (x2_new, y2_new),
                      (0, 255, 0), 2)

        cv2.putText(frame,
                    text,
                    (x1_new, y1_new - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2)

    # Tampilkan jumlah objek
    cv2.putText(frame,
                f'Jumlah Objek: {object_count}',
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2)

    cv2.imshow("YOLOv5 Live Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()