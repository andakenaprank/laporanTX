# === File: ocr_utils.py ===
import cv2
import pytesseract
import numpy as np
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def extract_text_from_box(image, box):
    x, y, w, h = box
    roi = image[y:y+h, x:x+w]
    roi = cv2.resize(roi, None, fx=5, fy=5, interpolation=cv2.INTER_LINEAR)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Izinkan angka, titik, spasi, dan huruf W (untuk "19 W")
    config = '--psm 6 -c tessedit_char_whitelist=0123456789.W '

    text = pytesseract.image_to_string(cleaned, config=config)

    # Ambil angka desimal (untuk 3.00) atau bilangan bulat (untuk 19 W)
    match = re.search(r'(\d+\.\d{2})', text)
    if not match:
      match = re.search(r'(\d{1,3})(\s*[wW])?', text)  # menangkap 19 W atau 19W


    return match.group(1) if match else ''


def detect_green_boxes_and_ocr(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return '', '', None

    image = cv2.resize(image, (640, 360))
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 30 < w < 300 and 20 < h < 150:
            boxes.append((x, y, w, h))
    boxes = sorted(boxes, key=lambda b: b[0])

    if len(boxes) < 2:
        return '', '', image

    fwd_box, refl_box = boxes[:2]
    forward_text = extract_text_from_box(image, fwd_box)
    reflected_text = extract_text_from_box(image, refl_box)
    return forward_text, reflected_text, image
