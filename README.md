# Part Counting Station Terintegrasi

Part Counting Station merupakan sistem verifikasi kuantitas part dalam kemasan transparan berbasis **Computer Vision**, **Sensor Fusion**, **Edge Computing**, dan **Industrial Monitoring Dashboard**.

Proyek ini dikembangkan untuk mengotomatisasi proses penghitungan part yang sebelumnya dilakukan secara manual. Sistem memanfaatkan model deteksi objek berbasis YOLOv5 untuk menghitung jumlah part secara real-time, kemudian memverifikasi hasil tersebut menggunakan sensor berat (Load Cell). Hasil inspeksi dikirim melalui MQTT ke backend FastAPI, disimpan ke database MySQL, dan divisualisasikan menggunakan dashboard Grafana Cloud.

Sistem dirancang untuk mengurangi human error, mempercepat proses inspeksi, mendukung traceability, serta menyediakan monitoring kualitas secara real-time pada lingkungan manufaktur.

---

## Latar Belakang

Pada proses manufaktur, inspeksi kuantitas part masih sering dilakukan secara manual. Metode ini memiliki beberapa kelemahan:

* Rentan terhadap human error.
* Membutuhkan waktu inspeksi yang lama.
* Sulit melakukan audit dan traceability.
* Tidak tersedia monitoring secara real-time.
* Berpotensi merusak kemasan saat proses pengecekan.

Part Counting Station dikembangkan untuk mengatasi permasalahan tersebut melalui pendekatan otomatis berbasis Computer Vision dan Sensor Fusion.

---

## Dokumentasi & Gambar Sistem

### Video Demo

Tonton video demonstrasi operasional sistem secara langsung melalui tautan berikut: 
👉 **[clips.id/EpsonA4-VideoDemo](https://clips.id/EpsonA4-VideoDemo)**

### Dashboard Monitoring KPI

![Dashboard Part Counting Station](https://drive.google.com/uc?export=view&id=1XLAQpQVraPZclW2MkgNAsjzll93XrNpZ)


### Produk Akhir

![Produk Akhir Part Counting Station](https://drive.google.com/uc?export=view&id=1ukeZ2dkpgETYAb1fUlEZITi6W86MSN3E)

---

## Fitur Utama

| Modul                   | Fitur                                                            |
| ----------------------- | ---------------------------------------------------------------- |
| AI Computer Vision      | Deteksi dan counting part menggunakan YOLOv5                     |
| Image Preprocessing     | CLAHE untuk mengurangi glare pada kemasan transparan             |
| Sensor Fusion           | Verifikasi jumlah part menggunakan Computer Vision dan Load Cell |
| Embedded System         | Raspberry Pi 5 sebagai edge computing device                     |
| Backend API             | FastAPI dan MQTT Subscriber                                      |
| Database                | Penyimpanan histori inspeksi dan audit trail menggunakan MySQL   |
| Dashboard Monitoring    | Monitoring KPI dan alerting menggunakan Grafana Cloud            |
| Real-Time Communication | MQTT dan REST API                                                |

---

## Arsitektur Sistem

```text
Raspberry Pi 5
(Camera + YOLOv5 + Load Cell)
            │
            │ MQTT
            ▼
      FastAPI Backend
            │
            ▼
      MySQL Database
            │
            ▼
      Grafana Cloud
```

Alur sistem:

1. Kamera mengambil citra part dalam kemasan.
2. YOLOv5 melakukan deteksi dan counting objek.
3. Load Cell membaca berat aktual kemasan.
4. Raspberry Pi mengirim hasil inspeksi melalui MQTT.
5. Backend FastAPI menerima payload dan menjalankan sensor fusion.
6. Hasil disimpan ke database MySQL.
7. Dashboard Grafana menampilkan KPI dan histori inspeksi secara real-time.

---

## Teknologi yang Digunakan

| Komponen           | Teknologi                               |
| ------------------ | --------------------------------------- |
| Bahasa Pemrograman | Python 3                                |
| Backend            | FastAPI                                 |
| Database           | MySQL                                   |
| ORM                | SQLAlchemy                              |
| MQTT               | Paho MQTT                               |
| AI Model           | YOLOv5                                  |
| Computer Vision    | OpenCV                                  |
| Framework AI       | PyTorch                                 |
| Dashboard          | Grafana Cloud                           |
| Edge Device        | Raspberry Pi 5                          |
| Kamera             | Camera Module 3                         |
| Sensor Berat       | Load Cell + HX711                       |                             
| Development Tools  | Google Colab, Jupyter Notebook, VS Code |

---

## AI Computer Vision

Sistem menggunakan YOLOv5 untuk mendeteksi dan menghitung jumlah part secara otomatis.

Jenis part yang digunakan pada penelitian:

* Spring
* Nut
* Screw

### Eksperimen Model

Beberapa pendekatan yang diuji:

* YOLOv5
* SSD MobileNet V2
* YOLOv5 + CLAHE
* YOLOv5 + SAHI

Hasil evaluasi menunjukkan bahwa YOLOv5 dengan preprocessing CLAHE memberikan performa terbaik untuk mendeteksi spring dalam kemasan transparan.

### Hasil Evaluasi

* mAP50 mencapai 99.1%
* YOLOv5 lebih stabil dibanding SSD MobileNet V2
* CLAHE berhasil mengurangi efek glare
* SAHI menghasilkan over-detection sehingga tidak digunakan pada pipeline final

---

## Sensor Fusion

Sistem menggunakan metode dual verification.

### Computer Vision

```python
n_cv
```

Jumlah objek hasil deteksi YOLOv5.

### Load Cell

```python
n_weight
```

Estimasi jumlah objek berdasarkan berat aktual.

### Validasi

```python
difference = abs(n_cv - n_weight)

status = "OK" if difference <= threshold else "NG"
```

Jika selisih masih berada dalam batas threshold, maka status inspeksi dinyatakan OK.

---

## Embedded System

Embedded system dijalankan pada Raspberry Pi 5.

Komponen utama:

* Raspberry Pi 5
* Camera Module 3
* Load Cell 10 Kg
* HX711
* OLED Display
* LED PWM

Fungsi embedded:

* Akuisisi gambar
* Inferensi YOLOv5
* Pembacaan berat
* Pengiriman data MQTT
* Menampilkan hasil inspeksi pada OLED

---

## Backend API

Backend dikembangkan menggunakan FastAPI.

Fungsi utama:

* MQTT Subscriber
* Sensor Fusion Processor
* REST API
* Database Integration
* Audit Trail Management

Contoh endpoint:

```http
GET /health
GET /parts
GET /inspections
```

---

## Database

Database menggunakan MySQL.

Tabel utama:

### part

Menyimpan informasi part:

* id
* part_name
* weight_per_unit
* target_qty
* threshold

### users

Menyimpan data pengguna sistem.

### inspections

Menyimpan histori inspeksi.

### inspection_details

View untuk kebutuhan dashboard dan reporting.

---

## Dashboard Monitoring

Dashboard dikembangkan menggunakan Grafana Cloud.

Fitur utama:

### KPI Dashboard

* Total Inspection
* Total OK
* Total NG
* Defect Rate

### Monitoring

* Grafik tren inspeksi
* Histori inspeksi
* Filter tanggal
* Detail discrepancy

### Export

* PDF
* CSV
* Image

### Alerting

Email alert dikirim ketika:

```text
Defect Rate > 10%
```

---

## MQTT Communication

Topic:

```text
capstone/A4/4
```

Contoh payload:

```json
{
  "part_id": 1,
  "user": "admin",
  "jumlah_objek": 25,
  "berat_g": 30.5,
  "timestamp": 1780648594.1958232
}
```

---

## Struktur Repository

```text
part-counting-station/
├── backend/                  
│   ├── app/
│   │   ├── main.py             
│   │   ├── api/v1/             
│   │   ├── core/              
│   │   ├── models/           
│   │   ├── schemas/           
│   │   └── services/         
│   ├── requirements.txt
│   └── .env.example
├── model/                     
│   ├── best.pt                  
│   ├── SSDMobileNetTraining.ipynb
│   └── TrainModelCapstone.ipynb
├── dashboard/                   
│   └── dashboard-part_counting_station.json
├── hardware/                    
│   └── capstoneA4_4_raspi5.py   
└── README.md
---

## Tim Pengembang

| Nama                             | Peran                                         |
| -------------------------------- | --------------------------------------------- |
| Stephanie Gabriella Wijaya       | Business Process Analyst                      |
| Maulana Aryan Wicaksana Sabandar | AI/ML Engineer                                |
| Nadhif Rif'at Rasendriya         | Computer Vision Engineer                      |
| Zaka Aulia Nala Udhma            | Hardware Engineer                             |
| Davin Kenaz Widiananda Tappo     | Hardware Engineer                             |
| Aulia Permata Kumala             | Backend Engineer                              |

---
