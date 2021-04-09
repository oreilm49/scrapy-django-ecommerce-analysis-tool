import cv2 as cv
from pdf2image import convert_from_path
from PIL import Image
import tempfile
from typing import Optional
import uuid

from cms.scraper.settings import IMAGES_ENERGY_LABELS_STORE


def small_pdf_2_image(download_url: str) -> str:
    """
    validates if string pass is a valid pdf url
    converts pdf url to image and saves in images folder
    returns path to image
    """
    file_extension: str = download_url[-3:]
    if file_extension != 'pdf':
        raise Exception(f"Download url is not a pdf link: '{download_url}'")
    with tempfile.TemporaryDirectory() as path:
        images = convert_from_path(download_url, output_folder=path)
        for image in images:
            path: str = f"{IMAGES_ENERGY_LABELS_STORE}/{uuid.uuid4()}.png"
            image.save(path)
            return path


def energy_label_cropped_2_qr(image_path: str) -> str:
    """
    2020 energy labels contain a qr code in the top right corner.
    This crops that from the image so the qr code can be processed later.
    """
    image = Image.open(image_path)
    image_width, image_height = image.size
    image.crop(box=(image_width / 2, 1, image_width, int(image_height * .25)))
    cropped = image.crop(box=(image_width / 2, 1, image_width, int(image_height * .25)))
    path: str = f"{image_path.split('.')[1]}_qr.png"
    cropped.save(path)
    return path


def read_qr(image_path: str) -> Optional[str]:
    """
    Reads data from a qr code image.
    For energy labels the below url should be expected:
    "https://eprel.ec.europa.eu/qr/298173"
    """
    image = cv.imread(image_path)
    detector = cv.QRCodeDetector()
    decoded_text, _, _ = detector.detectAndDecode(image)
    return decoded_text
