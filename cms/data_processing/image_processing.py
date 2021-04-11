import cv2 as cv
import os

import requests
from pdf2image import convert_from_path
from PIL import Image
import re
import tempfile
from typing import Optional
import uuid

from cms.scraper.settings import IMAGES_ENERGY_LABELS_STORE


def validate_pdf_url(download_url: str) -> str:
    """
    validates if download_url is a valid pdf.
    """
    response = requests.head(download_url)
    if response.status_code != 200:
        raise Exception(f"Download url return invalid response: '{download_url}' -> '{response.status_code}'")
    if response.headers['Content-Type'] != 'application/pdf':
        raise Exception(f"Download url is not a pdf link: '{download_url}'")
    return download_url


def small_pdf_2_image(download_url: str) -> str:
    """
    converts pdf url to image and saves in images folder
    returns path to image
    """
    download_url: str = validate_pdf_url(download_url)
    storage_folder_exists = os.path.isdir(IMAGES_ENERGY_LABELS_STORE)
    if not storage_folder_exists:
        os.makedirs(IMAGES_ENERGY_LABELS_STORE)
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
    path: str = f"{image_path.split('.')[0]}_qr.png"
    cropped.save(path)
    return path


def read_qr(image_path: str) -> Optional[str]:
    """
    Reads data from a qr code image.
    """
    image = cv.imread(image_path)
    detector = cv.QRCodeDetector()
    decoded_text, _, _ = detector.detectAndDecode(image)
    return decoded_text


def extract_eprel_code_from_url(url: str) -> Optional[str]:
    """
    For energy labels the below url should be expected:
    "https://eprel.ec.europa.eu/qr/298173"
    """
    return url[-6:] if re.match(r"^https:\/\/eprel\.ec\.europa\.eu\/qr\/\d{6}$", url) is not None else None
