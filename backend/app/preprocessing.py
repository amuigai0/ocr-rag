import os
import cv2
import logging
import numpy as np

"""

Per-processing file to clean JPEG images for OCR processing
"""

# Logging configs
logging.basicConfig(
    filename="pre_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_image(image_path): # Loads an image for preprocessing
    if not os.path.exist(image_path):
        logging.error(f"Image not found {image_path}")
        raise FileNotFoundError(f"Image not found {image_path}")
    
    image = cv2.imread(image_path)

    if image is None:
        logging.error(f"Failed to load image: {image_path}")
        raise ValueError(f"OpenCV failed to load image: {image_path}")

    logging.info(f"Image loaded successfully: {image_path}")
    return image


if __name__ == "__main__":
    image_path = r"../../gazettes/images/Kenya Gazette Vol CXVI No 129/Kenya Gazette Vol CXVI No 129 page 0.jpeg"