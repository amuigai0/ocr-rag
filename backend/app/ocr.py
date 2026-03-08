import os
import cv2
import logging
import numpy as np
from PIL import Image
import pytesseract

#Logs configuration
logging.basicConfig(
    filename="ocr_pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

original_img = r"../../gazettes/images/Kenya Gazette Vol CXVI No 129/Kenya Gazette Vol CXVI No 129 page 0.jpeg"
preprocessed_img = r"page0_processed.jpg"

img_1 = Image.open(original_img)
img_2 = Image.open(preprocessed_img)

ocr_result_1 = pytesseract.image_to_string(img_1)
ocr_result_2 = pytesseract.image_to_string(img_2)

print (ocr_result_2)