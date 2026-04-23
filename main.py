import cv2
import numpy as np
import glob
import os

DEBUG_DIR = "debug_output"
os.makedirs(DEBUG_DIR, exist_ok=True)

# nový threshold (laditeľný)
LENGTH_THRESHOLD = 3000   # celková dĺžka čiar

def analyze(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        print(f"ERROR: {img_path}")
        return

    # ===== EDGE =====
    blur = cv2.GaussianBlur(img, (5,5), 0)
    edges = cv2.Canny(blur, 30, 100)

    # ===== HOUGH =====
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi/180,
        threshold=50,
        minLineLength=40,
        maxLineGap=10
    )

    total_length = 0
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l[0]

            length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
            total_length += length

            cv2.line(vis, (x1,y1), (x2,y2), (0,0,255), 2)

    result = "PASS" if total_length < LENGTH_THRESHOLD else "FAIL"

    print(f"{img_path} -> length={int(total_length)}, result={result}")

    name = img_path.replace("/", "_").replace(".png", "")

    cv2.imwrite(f"{DEBUG_DIR}/{name}_edges.png", edges)
    cv2.imwrite(f"{DEBUG_DIR}/{name}_result.png", vis)


def run_all():
    images = glob.glob("pics/**/*.png", recursive=True)

    if len(images) == 0:
        print("❌ No images found")
        return

    print(f"✔ Found {len(images)} images")

    for img in images:
        analyze(img)


if __name__ == "__main__":
    run_all()