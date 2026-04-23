import cv2
import numpy as np
import os

INPUT_DIR = "pics"
OUTPUT_DIR = "output"
DEBUG_DIR = "debug_output"

THRESHOLD_LENGTH = 1500

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)


def load_images(folder):
    images = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".png"):
                images.append(os.path.join(root, f))
    return images


def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    return gray, blur


def detect_edges(blur):
    edges = cv2.Canny(blur, 30, 100)

    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    return edges


def remove_borders(edges):
    h, w = edges.shape

    mask = np.zeros_like(edges)
    margin_h = int(h * 0.07)
    margin_w = int(w * 0.07)

    mask[margin_h:h-margin_h, margin_w:w-margin_w] = 255

    return cv2.bitwise_and(edges, mask)


def get_roi_mask(gray):
    _, mask = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((25, 25), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


# 🔥 vlastný thinning (bez ximgproc)
def skeletonize(img):
    img = img.copy()
    skel = np.zeros(img.shape, np.uint8)

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

    while True:
        eroded = cv2.erode(img, kernel)
        temp = cv2.dilate(eroded, kernel)
        temp = cv2.subtract(img, temp)
        skel = cv2.bitwise_or(skel, temp)
        img = eroded.copy()

        if cv2.countNonZero(img) == 0:
            break

    return skel


def compute_length_metric(edges, roi):
    valid = cv2.bitwise_and(edges, roi)

    skeleton = skeletonize(valid)

    length = np.sum(skeleton > 0)

    return length, valid, skeleton


def draw_overlay(img, skeleton):
    result = img.copy()

    ys, xs = np.where(skeleton > 0)

    for (x, y) in zip(xs, ys):
        result[y, x] = [0, 0, 255]

    return result


def process_image(path):
    img = cv2.imread(path)

    gray, blur = preprocess(img)
    edges = detect_edges(blur)
    edges = remove_borders(edges)

    roi = get_roi_mask(gray)

    length, valid, skeleton = compute_length_metric(edges, roi)

    if length > THRESHOLD_LENGTH:
        result_label = "FAIL"
    else:
        result_label = "PASS"

    name = os.path.basename(path)

    cv2.imwrite(os.path.join(DEBUG_DIR, f"{name}_edges.png"), edges)
    cv2.imwrite(os.path.join(DEBUG_DIR, f"{name}_roi.png"), roi)
    cv2.imwrite(os.path.join(DEBUG_DIR, f"{name}_skeleton.png"), skeleton)

    result_img = draw_overlay(img, skeleton)
    cv2.imwrite(os.path.join(OUTPUT_DIR, f"{name}_result.png"), result_img)

    return length, result_label


def main():
    images = load_images(INPUT_DIR)

    if not images:
        print("❌ Žiadne obrázky sa nenašli v pics/")
        return

    print(f"✔ Found {len(images)} images\n")

    for img_path in images:
        length, result = process_image(img_path)

        print(f"{img_path} -> scratch_length={length}, result={result}")


if __name__ == "__main__":
    main()