import cv2
import pytesseract
import re

def extract_power_info(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return {}

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = "--psm 6"
    raw_text = pytesseract.image_to_string(thresh, config=config)
    print("[RAW OCR TEXT]\n", raw_text)

    result = {
        "RS": None, "RN": None, "ST": None, "SN": None, "TR": None, "TN": None, "freq": None,
        "arus": {"R": None, "S": None, "T": None}
    }

    mapping = {
        "L1-N": "RN", "L2-N": "SN", "L3-N": "TN",
        "L1-L2": "RS", "L2-L3": "ST", "L3-L1": "TR",
        "L1": "R", "L2": "S", "L3": "T"
    }

    for line in raw_text.splitlines():
        for key, target in mapping.items():
            if key in line:
                match = re.search(rf"{key}\s+(\d+[\.,]?\d*)", line)
                if match:
                    val = float(match.group(1).replace(',', '.'))
                    if target in result:
                        result[target] = val
                    elif target in result["arus"]:
                        result["arus"][target] = val

        if "Frequency" in line:
            freq_match = re.search(r"(\d+[\.,]?\d*)", line)
            if freq_match:
                result["freq"] = freq_match.group(1) + " Hz"

    return result
