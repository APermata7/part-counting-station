import sys
import time
import cv2
import torch
import RPi.GPIO as GPIO
import json
import paho.mqtt.client as mqtt

# ===============================
# Tambahkan path folder library
# ===============================
sys.path.append('./hx711py')

from hx711 import HX711

# ===============================
# Konfigurasi MQTT
# ===============================
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "capstone/A4/4"

# ===============================
# Daftar User
# ===============================
USERS = [
    "admin",
    "operator",
    "supervisor",
    "vendor"
]

# ===============================
# Daftar Part ID
# ===============================
PART_IDS = [1, 2, 3]

# ===============================
# Inisialisasi MQTT
# ===============================
client = mqtt.Client()

try:
    print("Menghubungkan ke broker MQTT...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    print("MQTT Connected")

except Exception as e:
    print(f"Gagal terhubung ke MQTT: {e}")
    sys.exit(1)

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
# Load YOLOv5 Local
# ===============================
model = torch.hub.load(
    './yolov5',
    'custom',
    path='best.pt',
    source='local'
)

print("YOLOv5 Ready")

# ===============================
# Kamera
# ===============================
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ===============================
# CLAHE Setup
# ===============================
clahe = cv2.createCLAHE(
    clipLimit=2.0,
    tileGridSize=(8, 8)
)

# ===============================
# Main Loop
# ===============================
try:

    while True:

        # ==================================================
        # PILIH USER
        # ==================================================
        print("\n==============================")
        print("PILIH USER")
        print("==============================")

        for i, user in enumerate(USERS):
            print(f"{i+1}. {user}")

        print("0. Keluar Program")

        while True:

            try:

                user_choice = int(
                    input("Masukkan pilihan user: ")
                )

                # ===========================
                # Keluar Program
                # ===========================
                if user_choice == 0:

                    print("Program selesai")
                    raise KeyboardInterrupt

                # ===========================
                # Pilihan User Valid
                # ===========================
                elif 1 <= user_choice <= len(USERS):

                    selected_user = USERS[user_choice - 1]
                    break

                else:
                    print("Pilihan tidak valid")

            except ValueError:
                print("Input harus angka")

        # ==================================================
        # PILIH PART ID
        # ==================================================
        print("\n==============================")
        print("PILIH PART ID")
        print("==============================")

        for i, part in enumerate(PART_IDS):
            print(f"{i+1}. Part ID {part}")

        print("0. Keluar Program")

        while True:

            try:

                part_choice = int(
                    input("Masukkan pilihan part ID: ")
                )

                # ===========================
                # Keluar Program
                # ===========================
                if part_choice == 0:

                    print("Program selesai")
                    raise KeyboardInterrupt

                # ===========================
                # Pilihan Part Valid
                # ===========================
                elif 1 <= part_choice <= len(PART_IDS):

                    part_id = PART_IDS[part_choice - 1]
                    break

                else:
                    print("Pilihan tidak valid")

            except ValueError:
                print("Input harus angka")

        print("\n==============================")
        print(f"User      : {selected_user}")
        print(f"Part ID   : {part_id}")
        print("==============================")

        # ==================================================
        # Reset / Tare Loadcell
        # ==================================================
        print("Melakukan tare loadcell...")

        hx.tare()

        time.sleep(2)

        # ==================================================
        # Timer Verifikasi
        # ==================================================
        verification_start = time.time()

        # ==================================================
        # Variabel Data Terakhir
        # ==================================================
        last_object_count = 0
        last_weight = 0

        while True:

            elapsed_time = time.time() - verification_start

            # ==================================================
            # Batas Verifikasi 15 Detik
            # ==================================================
            if elapsed_time >= 15:
                break

            ret, frame = cap.read()

            if not ret:
                print("Kamera tidak terdeteksi")
                break

            # ==================================================
            # CLAHE
            # ==================================================
            lab = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2LAB
            )

            l, a, b = cv2.split(lab)

            cl = clahe.apply(l)

            lab_clahe = cv2.merge((cl, a, b))

            frame_clahe = cv2.cvtColor(
                lab_clahe,
                cv2.COLOR_LAB2BGR
            )

            # ==================================================
            # Baca Berat
            # ==================================================
            weight = hx.get_weight(3)

            hx.power_down()
            hx.power_up()

            # ==================================================
            # YOLO Detection
            # ==================================================
            results = model(frame_clahe)

            detections = results.xyxy[0]

            object_count = len(detections)

            # ==================================================
            # Simpan Data Terakhir
            # ==================================================
            last_object_count = object_count
            last_weight = round(weight, 1)

            # ==================================================
            # Bounding Box
            # ==================================================
            for det in detections:

                x1, y1, x2, y2, conf, cls = det

                x1 = int(x1)
                y1 = int(y1)
                x2 = int(x2)
                y2 = int(y2)

                confidence = float(conf)

                class_id = int(cls)

                label = model.names[class_id]

                # ==================================================
                # Perkecil Bounding Box
                # ==================================================
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

                # ==================================================
                # Bounding Box
                # ==================================================
                cv2.rectangle(
                    frame_clahe,
                    (x1_new, y1_new),
                    (x2_new, y2_new),
                    (0, 255, 0),
                    2
                )

                # ==================================================
                # Label
                # ==================================================
                cv2.putText(
                    frame_clahe,
                    text,
                    (x1_new, y1_new - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

            # ==================================================
            # Informasi Kamera
            # ==================================================
            cv2.putText(
                frame_clahe,
                f'User: {selected_user}',
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2
            )

            cv2.putText(
                frame_clahe,
                f'Part ID: {part_id}',
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame_clahe,
                f'Jumlah Objek: {object_count}',
                (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

            cv2.putText(
                frame_clahe,
                f'Berat: {weight:.1f} g',
                (10, 135),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                2
            )

            remaining_time = int(
                15 - elapsed_time
            )

            cv2.putText(
                frame_clahe,
                f'Waktu: {remaining_time} s',
                (10, 170),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            # ==================================================
            # Tampilkan Kamera
            # ==================================================
            cv2.imshow(
                "YOLOv5 + HX711 + CLAHE",
                frame_clahe
            )

            # ==================================================
            # Tombol Keluar
            # ==================================================
            if cv2.waitKey(1) & 0xFF == ord('q'):
                raise KeyboardInterrupt

            time.sleep(0.05)

        # ==================================================
        # Payload MQTT
        # Kirim data terakhir
        # ==================================================
        payload = {

            "user": selected_user,

            "part_id": part_id,

            "jumlah_objek": last_object_count,

            "berat_g": last_weight,

            "timestamp": time.time()
        }

        client.publish(
            MQTT_TOPIC,
            json.dumps(payload)
        )

        print(f"\nMQTT FINAL -> {payload}")

        # ==================================================
        # Verifikasi selesai
        # ==================================================
        print("Verifikasi selesai")

        # ==================================================
        # Reset / Tare
        # ==================================================
        hx.tare()

        # ==================================================
        # Tampilan selesai
        # ==================================================
        verification_done_start = time.time()

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            # ==================================================
            # CLAHE
            # ==================================================
            lab = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2LAB
            )

            l, a, b = cv2.split(lab)

            cl = clahe.apply(l)

            lab_clahe = cv2.merge((cl, a, b))

            frame_clahe = cv2.cvtColor(
                lab_clahe,
                cv2.COLOR_LAB2BGR
            )

            # ==================================================
            # Tampilkan status
            # ==================================================
            cv2.putText(
                frame_clahe,
                "VERIFIKASI SELESAI",
                (120, 220),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3
            )

            cv2.putText(
                frame_clahe,
                "LOADCELL RESET / TARE",
                (90, 270),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2
            )

            cv2.imshow(
                "YOLOv5 + HX711 + CLAHE",
                frame_clahe
            )

            if cv2.waitKey(1) & 0xFF == ord('q'):
                raise KeyboardInterrupt

            # tampil 3 detik
            if time.time() - verification_done_start >= 3:
                break

        print("Kembali ke menu pemilihan")

except KeyboardInterrupt:

    print("Program dihentikan")

finally:

    # ===============================
    # Cleanup
    # ===============================
    cap.release()

    cv2.destroyAllWindows()

    GPIO.cleanup()

    client.loop_stop()

    client.disconnect()

    print("Koneksi MQTT diputuskan.")