# Part Counting Station

Part Counting Station adalah sebuah proyek berbasis Computer Vision yang dirancang untuk menghitung jumlah komponen atau *parts* secara otomatis dan *real-time*. Proyek ini memanfaatkan model deteksi objek *deep learning* untuk meningkatkan efisiensi dan akurasi dalam proses penghitungan, sangat cocok untuk diimplementasikan dalam skenario manufaktur atau logistik.

## Fitur Utama
* **Deteksi Objek Cepat & Akurat**: Menggunakan model *state-of-the-art* (seperti YOLO/PyTorch dan SSD MobileNet) untuk mendeteksi dan mengklasifikasikan berbagai jenis *parts*.
* **Penghitungan Real-Time**: Mampu menghitung jumlah objek secara langsung dari *feed* kamera atau video simulasi.
* **Custom Model Training**: Menyediakan struktur *notebook* yang terorganisir untuk melatih model menggunakan dataset kustom.

## Teknologi yang Digunakan
* **Bahasa Pemrograman**: Python 3
* **Computer Vision**: OpenCV
* **Deep Learning Framework**: PyTorch (untuk model berekstensi `.pt`), TensorFlow/Keras (untuk SSD MobileNet)
* **Environment**: Jupyter Notebook

## Prasyarat Instalasi
Pastikan Anda telah menginstal Python 3.8 atau versi yang lebih baru di sistem Anda.

1. Kloning repositori ini ke komputer lokal Anda:
```bash
git clone [https://github.com/apermata7/part-counting-station.git](https://github.com/apermata7/part-counting-station.git)
cd part-counting-station
```


2. Buat dan aktifkan *virtual environment* (opsional namun sangat direkomendasikan):
```bash
python -m venv venv

# Untuk pengguna Linux/Mac:
source venv/bin/activate  

# Untuk pengguna Windows:
venv\Scripts\activate

```


3. Instal dependensi library dasar yang dibutuhkan:
```bash
pip install torch torchvision torchaudio opencv-python pandas jupyter

```


*(Catatan: Anda mungkin perlu menambahkan framework tambahan seperti TensorFlow sesuai dengan kebutuhan komputasi atau versi CUDA Anda)*

## Susunan Project

Berikut adalah struktur direktori utama dari proyek ini:

```
part-counting-station/
├── model/
│   ├── best.pt                        # Bobot (weights) model terlatih terbaik
│   ├── SSDMobileNetTraining.ipynb     # Notebook untuk eksperimen training model SSD MobileNet
│   └── TrainModelCapstone.ipynb       # Notebook utama untuk memproses pipeline training
└── README.md                          # Dokumentasi utama proyek

```

## Contoh Penggunaan

1. **Melakukan Training / Evaluasi Model**:
Buka Jupyter Notebook untuk melihat, mengevaluasi, atau memodifikasi proses *training*.
```bash
jupyter notebook

```
Akses `model/TrainModelCapstone.ipynb` atau `model/SSDMobileNetTraining.ipynb` dari *browser* Anda.
2. **Menjalankan Inferensi**:
*(Catatan: Asumsi Anda akan membuat atau telah memiliki skrip inferensi seperti `detect.py`)*
Gunakan model `best.pt` untuk mendeteksi *parts* dari kamera web atau video:
```bash
python detect.py --weights model/best.pt --source 0  # Angka 0 digunakan untuk akses webcam

```



## Kontribusi

Kontribusi dari komunitas sangat diterima untuk mengembangkan proyek ini! Langkah-langkah untuk berkontribusi:

1. Lakukan *Fork* pada repositori ini.
2. Buat *branch* untuk fitur baru Anda (`git checkout -b fitur-baru`).
3. Lakukan *Commit* terhadap perubahan Anda (`git commit -m 'Menambahkan fitur deteksi baru'`).
4. *Push* ke *branch* tersebut (`git push origin fitur-baru`).
5. Buat sebuah *Pull Request* agar bisa direview.

## Lisensi

Proyek ini didistribusikan di bawah **MIT License**. Anda bebas untuk menggunakan, menyalin, memodifikasi, menggabungkan, menerbitkan, mendistribusikan, mensublisensikan, dan/atau menjual salinan perangkat lunak ini dengan menyertakan pemberitahuan hak cipta asli.
