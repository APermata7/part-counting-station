import time
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# Konfigurasi Dimensi Layar
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
FRAME_DELAY = 0.05  # Delay antar frame dalam detik

# Inisialisasi Hardware menggunakan port=0 (Pin 27 & 28)
try:
    # Menggunakan port=0 untuk I2C-0 di alamat default 0x3C
    serial = i2c(port=0, address=0x3C)
    device = ssd1306(serial, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    print("OLED SSD1306 pada I2C-0 (Pin 27,28) Berhasil Terhubung!")
except Exception as e:
    print(f"Gagal mendeteksi OLED. Periksa kabel atau pastikan dtparam=i2c_vc=on sudah aktif. Error: {e}")
    exit()

# Variabel animasi
posisi_x = 0
arah = 1

print("Menjalankan animasi sederhana... Tekan Ctrl+C untuk berhenti.")

try:
    while True:
        start_time = time.time()
        
        # Menggambar ke layar (Otomatis clear & display)
        with canvas(device) as draw:
            # Teks Judul
            draw.text((5, 2), "Sistem Siap (I2C-0)", fill="white")
            
            # Kotak luar pembatas
            draw.rectangle((0, 16, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1), outline="white", fill="black")
            
            # Animasi kotak bergerak di dalam pembatas
            draw.rectangle((posisi_x, 30, posisi_x + 12, 45), outline="white", fill="white")
            
        # Logika pergerakan kotak
        posisi_x += 5 * arah
        
        # Memantul jika mengenai ujung kanan/kiri kotak pembatas
        if posisi_x >= (SCREEN_WIDTH - 15) or posisi_x <= 2:
            arah *= -1
            
        # Mengatur FPS agar stabil
        elapsed_time = time.time() - start_time
        if elapsed_time < FRAME_DELAY:
            time.sleep(FRAME_DELAY - elapsed_time)

except KeyboardInterrupt:
    device.clear()
    print("\nProgram dihentikan, layar dibersihkan.")