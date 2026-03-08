import os
import cv2
import logging
import numpy as np

"""
Pre-processing file to clean JPEG images for OCR processing
"""

# Logging configs
logging.basicConfig(
    filename="pre_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_image(image_path):
    if not os.path.exists(image_path):
        logging.error(f"Image not found: {image_path}")
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = cv2.imread(image_path)
    if image is None:
        logging.error(f"Failed to load image: {image_path}")
        raise ValueError(f"Failed to load image: {image_path}")

    logging.info(f"Loaded image: {image_path}")
    return image


def preview_image(image, title="Preview", max_width=1200):
    h, w = image.shape[:2]

    if w > max_width:
        scale = max_width / w
        image = cv2.resize(image, (int(w * scale), int(h * scale)))

    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def crop_dark_edges(image, edge_margin=100, dark_threshold=35):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    top = 0
    for y in range(min(edge_margin, h)):
        if np.mean(gray[y, :]) > dark_threshold:
            top = y
            break

    bottom = h
    for y in range(h - 1, max(h - edge_margin - 1, 0), -1):
        if np.mean(gray[y, :]) > dark_threshold:
            bottom = y + 1
            break

    left = 0
    for x in range(min(edge_margin, w)):
        if np.mean(gray[:, x]) > dark_threshold:
            left = x
            break

    right = w
    for x in range(w - 1, max(w - edge_margin - 1, 0), -1):
        if np.mean(gray[:, x]) > dark_threshold:
            right = x + 1
            break

    cropped = image[top:bottom, left:right]
    logging.info(f"Cropped image from {image.shape} to {cropped.shape}")
    return cropped


def create_manual_artifact_mask(image):
    """
    Build a mask for the known page-0 artifacts:
    - left edge ink blob
    - diagonal 'National Council for Law Reporting' stamp
    Protect the title region by not masking there.
    """
    h, w = image.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    # 1. Left edge ink blob
    # Adjust these coordinates if needed
    cv2.rectangle(mask, (0, 180), (70, 620), 255, -1)

    # 2. Diagonal stamp region
    # Use a polygon to approximate the visible stamp
    stamp_polygon = np.array([
        [700, 120],
        [970, 20],
        [1010, 110],
        [760, 230]
    ], dtype=np.int32)

    cv2.fillPoly(mask, [stamp_polygon], 255)

    # 3. Protect title region by clearing mask there
    # Adjust if your title sits slightly differently after cropping
    cv2.rectangle(mask, (120, 240), (900, 470), 0, -1)

    return mask


def remove_artifacts_with_mask(image, mask):
    cleaned = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)
    return cleaned


def deskew_image_hough(image):
    """
    Estimate skew using near-horizontal lines.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    binary = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    lines = cv2.HoughLinesP(
        binary,
        1,
        np.pi / 180,
        threshold=180,
        minLineLength=300,
        maxLineGap=20
    )

    angles = []

    if lines is not None:
        for line in lines[:300]:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))

            if -10 < angle < 10:
                angles.append(angle)

    if not angles:
        logging.warning("No suitable lines found for deskew.")
        return image, 0.0

    median_angle = float(np.median(angles))

    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)

    rotated = cv2.warpAffine(
        image,
        M,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    logging.info(f"Deskew angle applied: {median_angle:.3f}")
    return rotated, median_angle


def preprocess_page0(image):
    cropped = crop_dark_edges(image)

    manual_mask = create_manual_artifact_mask(cropped)
    cleaned = remove_artifacts_with_mask(cropped, manual_mask)

    deskewed, angle = deskew_image_hough(cleaned)

    gray = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)

    processed = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        12
    )

    return {
        "cropped": cropped,
        "artifact_mask": manual_mask,
        "cleaned": cleaned,
        "deskewed": deskewed,
        "gray": gray,
        "processed": processed,
        "angle": angle,
    }


if __name__ == "__main__":
    image_path = r"../../gazettes/images/Kenya Gazette Vol CXVI No 129/Kenya Gazette Vol CXVI No 129 page 0.jpeg"

    image = load_image(image_path)
    results = preprocess_page0(image)

    print("Deskew angle:", results["angle"])

    preview_image(image, "Original")
    preview_image(results["cropped"], "Cropped")
    preview_image(results["artifact_mask"], "Artifact Mask")
    preview_image(results["cleaned"], "Cleaned")
    preview_image(results["deskewed"], "Deskewed")
    preview_image(results["processed"], "Processed")

    cv2.imwrite("page0_artifact_mask.jpg", results["artifact_mask"])
    cv2.imwrite("page0_cleaned.jpg", results["cleaned"])
    cv2.imwrite("page0_processed.jpg", results["processed"])