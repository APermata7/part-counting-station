import cv2
from ultralytics import YOLO

# Load model (pilih salah satu)
model = YOLO("best.pt")  
# atau kalau kamu punya model sendiri:
# model = YOLO("best.pt")

# Buka kamera (0 = /dev/video0)
cap = cv2.VideoCapture(0)

# Optional: set resolusi biar ringan
cap.set(3, 640)
cap.set(4, 480)

if not cap.isOpened():
    print("Kamera tidak bisa dibuka")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Inference YOLO
    results = model(frame)

    # Ambil frame dengan bounding box
    annotated_frame = results[0].plot()

    # Tampilkan
    cv2.imshow("YOLO Live Detection", annotated_frame)

    # Tekan 'q' untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()