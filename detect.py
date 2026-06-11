import tensorflow as tf
import numpy as np
import cv2
import matplotlib.pyplot as plt

# Path ke model dan gambar
PATH_TO_SAVED_MODEL = "e:/spring-detector/exported-model/saved_model"
IMAGE_PATH = r"C:\Users\MAULANA ARYAN\Downloads\WhatsApp Image 2026-05-08 at 1.41.52 PM.jpeg"
MIN_SCORE_THRESH = 0.5 # Ambang batas skor untuk menampilkan deteksi

# Muat model
print("Loading model...", end='')
detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
print("Done!")

# Muat gambar dan ubah menjadi tensor
print(f"Memuat gambar dari: {IMAGE_PATH}")
image_np = cv2.imread(IMAGE_PATH)

# Periksa apakah gambar berhasil dimuat
if image_np is None:
    print(f"Error: Tidak dapat memuat gambar dari path: {IMAGE_PATH}")
    print("Pastikan path file sudah benar dan file gambar tidak rusak.")
    exit()

print("Gambar berhasil dimuat.")
image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
input_tensor = tf.convert_to_tensor(image_np)
input_tensor = input_tensor[tf.newaxis, ...]

# Lakukan deteksi
print("Melakukan deteksi...")
detections = detect_fn(input_tensor)
print("Deteksi selesai.")

# Proses hasil deteksi
num_detections = int(detections.pop('num_detections'))
detections = {key: value[0, :num_detections].numpy()
              for key, value in detections.items()}
detections['num_detections'] = num_detections

# Ubah tipe data kelas deteksi menjadi integer
detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

# Visualisasikan hasil
print("Memvisualisasikan hasil...")
image_with_detections = image_np.copy()
boxes = detections['detection_boxes']
classes = detections['detection_classes']
scores = detections['detection_scores']

im_height, im_width, _ = image_with_detections.shape

for i in range(min(boxes.shape[0], 100)):
    if scores[i] > MIN_SCORE_THRESH:
        ymin, xmin, ymax, xmax = tuple(boxes[i].tolist())
        (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                                      ymin * im_height, ymax * im_height)
        
        # Gambar kotak
        cv2.rectangle(image_with_detections, (int(left), int(top)), (int(right), int(bottom)), (0, 255, 0), 2)
        
        # Tulis label dan skor
        label = f"spring: {int(scores[i]*100)}%"
        cv2.putText(image_with_detections, label, (int(left), int(top) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Tampilkan gambar hasil deteksi
print("Menampilkan gambar...")
plt.figure(figsize=(12, 8))
plt.imshow(image_with_detections)
plt.title("Hasil Deteksi")
plt.axis('off')
plt.show()

print("Skrip selesai. Jendela gambar seharusnya sudah ditampilkan.")
