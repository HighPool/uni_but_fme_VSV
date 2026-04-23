import cv2
import numpy as np
import os

# ===== PARAMETRE =====
THRESH_DIFF = 12
THRESH_BINARY = 30
MIN_DEFECT_AREA = 100

# ===== CESTY =====
BASE_DIR = "pics"
REF_PATH = os.path.join(BASE_DIR, "clean", "clean_Image_1.png")

# ===== REFERENCIA =====
ref = cv2.imread(REF_PATH, cv2.IMREAD_GRAYSCALE)

def process_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    # resize na referenciu
    img = cv2.resize(img, (ref.shape[1], ref.shape[0]))

    # rozdiel
    diff = cv2.absdiff(ref, img)
    score = np.mean(diff)

    # threshold
    _, thresh = cv2.threshold(diff, THRESH_BINARY, 255, cv2.THRESH_BINARY)

    # odstránenie šumu
    kernel = np.ones((3,3), np.uint8)
    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # kontúry
    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    defects = [c for c in contours if cv2.contourArea(c) > MIN_DEFECT_AREA]

    # rozhodnutie
    if score > THRESH_DIFF or len(defects) > 10:
        result = "FAIL"
    else:
        result = "PASS"

    return score, len(defects), result


# ===== SPRACOVANIE =====
results = []

for category in ["clean", "bad", "semibad"]:
    folder = os.path.join(BASE_DIR, category)

    for file in os.listdir(folder):
        if file.endswith(".png"):
            path = os.path.join(folder, file)

            score, defects, result = process_image(path)

            print(f"{category}/{file} -> score={score:.2f}, defects={defects}, result={result}")

            results.append((category, file, score, defects, result))


# ===== ULOŽENIE VÝSLEDKOV =====
with open("results.csv", "w") as f:
    f.write("category,file,score,defects,result\n")
    for r in results:
        f.write(f"{r[0]},{r[1]},{r[2]:.2f},{r[3]},{r[4]}\n")

print("\nResults saved to results.csv")