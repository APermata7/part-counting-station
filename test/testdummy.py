import sys
import time
import json
import random
import paho.mqtt.client as mqtt

# Note: RPi.GPIO dan library sensor/kamera dihapus agar bisa jalan tanpa hardware

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

print("Sistem Simulasi Ready (Tanpa Kamera & HX711)")

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
                user_choice = int(input("Masukkan pilihan user: "))

                # Keluar Program
                if user_choice == 0:
                    print("Program selesai")
                    raise KeyboardInterrupt

                # Pilihan User Valid
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

                # Keluar Program
                if part_choice == 0:
                    print("Program selesai")
                    raise KeyboardInterrupt

                # Pilihan Part Valid
                elif 1 <= part_choice <= len(PART_IDS):
                    part_id = PART_IDS[part_choice - 1]
                    break
                else:
                    print("Pilihan tidak valid")
            except ValueError:
                print("Input should be a number")

        print("\n==============================")
        print(f"User      : {selected_user}")
        print(f"Part ID   : {part_id}")
        print("==============================")

        # ==================================================
        # Simulasi Timer Verifikasi (15 Detik)
        # ==================================================
        print("Memulai proses verifikasi simulasi selama 5 detik...")
        verification_start = time.time()

        last_object_count = 0
        last_weight = 0.0

        while True:
            elapsed_time = time.time() - verification_start

            if elapsed_time >= 5:
                break

            # Generasi Data Dummy secara Real-time sesuai range
            # jumlah_objek: 20 s/d 29
            object_count = random.randint(20, 29)
            # berat_g: 25 s/d 38 (dibulatkan 1 desimal)
            weight = round(random.uniform(25.0, 38.0), 1)

            # Simpan Data Terakhir
            last_object_count = object_count
            last_weight = weight

            # Tampilkan log simulasi ke Terminal (Menggantikan overlay cv2.putText)
            remaining_time = int(5 - elapsed_time)
            print(f"[Simulasi] Waktu: {remaining_time}s | Jml Objek: {object_count} | Berat: {weight} g", end="\r")
            
            time.sleep(1) # Delay 1 detik per update di terminal
        
        print("\n[Simulasi] Proses pembacaan selesai.")

        # ==================================================
        # Payload MQTT (Kirim data terakhir)
        # ==================================================
        payload = {
            "user": selected_user,
            "part_id": part_id,
            "jumlah_objek": last_object_count,
            "berat_g": last_weight,
            "timestamp": time.time()
        }

        client.publish(MQTT_TOPIC, json.dumps(payload))
        print(f"\nMQTT FINAL -> {payload}")
        print("Verifikasi selesai")

        # ==================================================
        # Tampilan Selesai (Simulasi Delay 3 Detik)
        # ==================================================
        print("\n--- STATUS: VERIFIKASI SELESAI ---")
        print("--- STATUS: LOADCELL RESET / TARE (SIMULASI) ---")
        time.sleep(3)

        print("Kembali ke menu pemilihan")

except KeyboardInterrupt:
    print("\nProgram dihentikan")

finally:
    # ===============================
    # Cleanup (Hanya MQTT)
    # ===============================
    client.loop_stop()
    client.disconnect()
    print("Koneksi MQTT diputuskan.")