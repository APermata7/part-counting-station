import sys
import time
import cv2
import torch
import RPi.GPIO as GPIO
import json
import paho.mqtt.client as mqtt

import warnings

# Abaikan FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning)

# Library untuk OLED SSD1306 (I2C-0 Port 0)
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# ===============================
# Path folder library
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
# Daftar User & Part ID
# ===============================
USERS = ["admin", "operator"]
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
# Setup OLED SSD1306 (I2C-0 Port 0)
# ===============================
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

try:
    # Port=0 untuk Pin 27 (SDA) & Pin 28 (SCL)
    serial = i2c(port=0, address=0x3C)
    oled_device = ssd1306(serial, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    print("OLED SSD1306 Ready (I2C-0)")
except Exception as e:
    print(f"Gagal mendeteksi OLED di I2C-0. Error: {e}")
    sys.exit(1)

# ===============================
# Setup HX711 (Pin 5 & 6)
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
    source='local',
    skip_validation=True
)
print("YOLOv5 Ready")

# ===============================
# Kamera & CLAHE Setup
# ===============================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# ==================================================
# Update Tampilan OLED
# ==================================================
def update_oled(qty, weight, status_str):
    """
    qty: Jumlah objek (int)
    weight: Berat dalam gram (float)
    status_str: Status kelayakan "OK", "NG", atau "WAIT" (string)
    """
    with canvas(oled_device) as draw:
        draw.line((0, 0, SCREEN_WIDTH, 0), fill="white")
        draw.line((0, 15, SCREEN_WIDTH, 15), fill="white")
        draw.line((0, 63, SCREEN_WIDTH, 63), fill="white")
        
        draw.text((5, 2), f"QTY: {qty}", fill="white")
        draw.text((75, 2), f"{weight:.1f}g", fill="white")
        
        text_w = 40 if status_str in ["OK", "NG"] else 60
        text_x = int((SCREEN_WIDTH - text_w) / 2)
        text_y = 30
        
        draw.text((text_x, text_y), f"[{status_str}]", fill="white")

try:
    while True:
        update_oled(0, 0.0, "WAIT")

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
                user_choice = int(input("Masukkan pilihan user: "))
                if user_choice == 0:
                    print("Program selesai")
                    raise KeyboardInterrupt
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
                part_choice = int(input("Masukkan pilihan part ID: "))
                if part_choice == 0:
                    print("Program selesai")
                    raise KeyboardInterrupt
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

        verification_start = time.time()

        last_object_count = 0
        last_weight = 0
        final_status = "NG"

        print("Memulai verifikasi 15 detik... Silakan letakkan objek.")

        while True:
            elapsed_time = time.time() - verification_start

            if elapsed_time >= 15:
                break

            ret, frame = cap.read()
            if not ret:
                print("Kamera tidak terdeteksi")
                break

            # Preprocessing CLAHE
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            cl = clahe.apply(l)
            lab_clahe = cv2.merge((cl, a, b))
            frame_clahe = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)

            # Baca Berat
            weight = hx.get_weight(3)
            hx.power_down()
            hx.power_up()

            # YOLO Detection
            results = model(frame_clahe)
            detections = results.xyxy[0]
            object_count = len(detections)

            last_object_count = object_count
            last_weight = round(weight, 1)

            # ==================================================
            # LOGIKA VALIDASI (OK / NG) + TOLERANSI 4 GRAM
            # ==================================================
            berat_ideal = 1.22 * object_count
            batas_bawah = berat_ideal - 4.0
            batas_atas = berat_ideal + 4.0

            if object_count > 0 and (batas_bawah <= weight <= batas_atas):
                status_verifikasi = "OK"
            else:
                status_verifikasi = "NG"

            final_status = status_verifikasi

            update_oled(object_count, weight, status_verifikasi)

            remaining_time = int(15 - elapsed_time)
            print(f"[Verifikasi] Waktu sisa: {remaining_time}s | QTY: {object_count} | Berat: {weight:.1f}g | Status: {status_verifikasi}", end="\r")

            time.sleep(0.05)

        print("\nVerifikasi selesai, memproses data...")

        # ==================================================
        # Payload MQTT & Pengiriman Data
        # ==================================================
        payload = {
            "user": selected_user,
            "part_id": part_id,
            "jumlah_objek": last_object_count,
            "berat_g": last_weight,
            "status": final_status,
            "timestamp": time.time()
        }

        client.publish(MQTT_TOPIC, json.dumps(payload))
        print(f"MQTT FINAL -> {payload}")

        # Reset Timbangan
        hx.tare()

        # ==================================================
        # Tampilan Akhir Selesai di OLED 3 Detik
        # ==================================================
        print("Menampilkan hasil final di OLED selama 3 detik...")
        verification_done_start = time.time()
        while True:
            update_oled(last_object_count, last_weight, final_status)
            
            time.sleep(0.1)
            if time.time() - verification_done_start >= 3:
                break

        print("Kembali ke menu pemilihan...")

except KeyboardInterrupt:
    print("\nProgram dihentikan oleh pengguna.")

finally:
    try:
        oled_device.clear()
        print("Layar OLED dibersihkan.")
    except:
        pass
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
    print("Koneksi diputuskan, semua modul dibersihkan.")
