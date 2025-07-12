import cv2
import numpy as np

def detect_active_exciter(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return 'UNKNOWN'

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold untuk garis hitam tebal
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

    # Coba deteksi kontur panjang (garis dari selector)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / float(h)

        # Cari garis horizontal tebal yang menonjol ke arah Exciter A/B
        if 100 < w < 300 and 5 < h < 30 and aspect_ratio > 4:
            # Analisis lokasi vertikalnya
            if y > 200:  # posisi Exciter B
                return 'B'
            elif y < 200:  # posisi Exciter A
                return 'A'

    return 'UNKNOWN'
