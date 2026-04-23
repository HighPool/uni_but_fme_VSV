import cv2
import numpy as np
import os

# ===== PARAMETRE =====
THRESH_BINARY = 30
MIN_DEFECT_AREA = 100
PASS_THRESHOLD = 2.5  # % poškodenia

# ===== CESTY =====
BASE_DIR = "pics"
REF_IMAGES = [
    "clean/clean_Image_1.png",
    "clean/clean_Image_2.png",
    "clean/clean_Image_3.png"
]

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===== VYTVORENIE REFERENCIE (PRIEMER) =====
refs = []
for path in REF_IMAGES:
    img = cv2.imread(os.path.join(BASE_DIR, path), cv2.IMREAD_GRAYSCALE)
    refs.append(img)

ref = np.mean(refs, axis=0).astype(np.uint8)

# ===== ANALÝZA OBRAZU =====
def analyze_damage(img):
    img = cv2.resize(img, (ref.shape[1], ref.shape[0]))

    diff = cv2.absdiff(ref, img)

    _, thresh = cv2.threshold(diff, THRESH_BINARY, 255, cv2.THRESH_BINARY)

    kernel = np.ones((3,3), np.uint8)
    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    damage_pixels = np.sum(clean > 0)
    total_pixels = clean.size

    damage_percent = (damage_pixels / total_pixels) * 100
    quality_score = 100 - damage_percent

    return clean, damage_percent, quality_score

# ===== VIZUALIZÁCIA =====
def visualize_defects(img, mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    for c in contours:
        if cv2.contourArea(c) > MIN_DEFECT_AREA:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 0, 255), 2)

    return output

# ===== SPRACOVANIE =====
results = []

for category in ["clean", "bad", "semibad"]:
    folder = os.path.join(BASE_DIR, category)

    for file in os.listdir(folder):
        if file.endswith(".png"):
            path = os.path.join(folder, file)

            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

            mask, damage, quality = analyze_damage(img)

            if damage > PASS_THRESHOLD:
                result = "FAIL"
            else:
                result = "PASS"

            vis = visualize_defects(img, mask)

            # ===== ULOŽENIE OBRÁZKA =====
            save_path = os.path.join(OUTPUT_DIR, f"{category}_{file}")
            cv2.imwrite(save_path, vis)

            print(f"{category}/{file} -> damage={damage:.2f}%, quality={quality:.2f}%, result={result}")

            results.append((category, file, damage, quality, result))

# ===== CSV =====
with open("results.csv", "w") as f:
    f.write("category,file,damage_percent,quality_score,result\n")
    for r in results:
        f.write(f"{r[0]},{r[1]},{r[2]:.2f},{r[3]:.2f},{r[4]}\n")

print("\nSaved visualizations to /output folder")