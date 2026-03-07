import os
import logging
from pdf2image import convert_from_path

#Logs configuration
logging.basicConfig(
    filename="pdf_to_image_converter.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def pdf_to_img(pdf_path, output_folder="../../gazettes/images", dpi=300):
        if not os.path.exists(pdf_path):
                logging.error(f"PDF not found: {pdf_path}")
                raise FileNotFoundError(f"PDF not found: {pdf_path}")

        pdf_name = os.path.splitext(os.path.basename(pdf_path)) [0]

        pdf_output_folder = os.path.join(output_folder, pdf_name)
        os.makedirs(pdf_output_folder, exist_ok=True)

        logging.info(f"Processing PDF: {pdf_path}")
        logging.info(f"Created/using folder: {pdf_output_folder}")

        trace_data = []

        try:
            pages = convert_from_path(pdf_path, dpi=dpi)
            logging.info(f"Total pages in {pdf_name}: {len(pages)}")

            for i, page in enumerate(pages):
                image_name = f"{pdf_name} page {i}.jpeg"
                image_path = os.path.join(pdf_output_folder, image_name)

                page.save(image_path, "JPEG")

                trace_data.append({
                    "source_pdf": pdf_path,
                    "pdf_name": pdf_name,
                    "page_number": i,
                    "image_path": image_path
                })

                logging.info(f"Saved image: {image_path}")

            logging.info(f"Finished processing {pdf_name}")
            return trace_data

        except Exception as e:
            logging.exception(f"Error processing {pdf_path}: {e}")
            raise

if __name__ == "__main__":
      pdf_file = r"../../gazettes\pdf\2014\october\Kenya Gazette Vol CXVI No 129.pdf"
      results = pdf_to_img(pdf_file)

      for item in results:
            print(item)