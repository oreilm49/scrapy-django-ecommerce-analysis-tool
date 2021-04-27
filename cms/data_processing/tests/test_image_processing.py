import os

import requests
from django.test import TestCase

from cms.data_processing.image_processing import small_pdf_2_image, energy_label_cropped_2_qr, read_qr, \
    extract_eprel_code_from_url, validate_pdf_url, ContentTypeImageException
from cms.scraper.settings import IMAGES_ENERGY_LABELS_STORE


class TestImageProcessing(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.image_path = "/app/cms/data_processing/tests/data/label.png"
        cls.pdf_url = "https://cc.isitetv.com/clients/wp/whirlpool/859991530490/documentation/eur/whirlpool-fwl71253wuk-energy-label-el859991530490.pdf"
        cls.image_url = "https://www.miele.ie/pmedia/ZEN/100264825-EU-00_11358760.4002516248538.EU01.Energylabel.png"

    def test_validate_pdf_url(self):
        with self.subTest("content type validation"):
            with self.assertRaises(ContentTypeImageException) as context:
                validate_pdf_url("https://www.specr.ie/images/pivot_table.png")
            self.assertEqual(context.exception.content_type, "image/png")

        with self.subTest("invalid http response"):
            with self.assertRaises(Exception) as context:
                validate_pdf_url("http://google.com")
            self.assertEqual((str(context.exception)), "Download url return invalid response: 'http://google.com' -> '301'")

        with self.subTest("valid pdf url"):
            self.assertEqual(self.pdf_url, validate_pdf_url(self.pdf_url))

    def test_small_pdf_2_image(self):
        with self.subTest("url valid"):
            self.assertEqual(requests.get(self.pdf_url).status_code, 200)

        with self.subTest("valid pdf"):
            image_path = small_pdf_2_image(self.pdf_url)
            self.assertIn(IMAGES_ENERGY_LABELS_STORE, image_path)
            self.assertIn('.png', image_path)
            open(image_path)

        with self.subTest("image url"):
            image_path = small_pdf_2_image(self.image_url)
            self.assertIn(IMAGES_ENERGY_LABELS_STORE, image_path)
            self.assertIn('.png', image_path)
            open(image_path)

    def test_energy_label_cropped_2_qr(self):
        cropped_image_path = energy_label_cropped_2_qr(self.image_path)
        self.assertEqual("/app/cms/data_processing/tests/data/label_qr.png", cropped_image_path)
        open(cropped_image_path)
        os.remove(cropped_image_path)

    def test_read_qr(self):
        with self.subTest("image path"):
            cropped_image_path = energy_label_cropped_2_qr(self.image_path)
            decoded_text = read_qr(cropped_image_path)
            self.assertEqual("https://eprel.ec.europa.eu/qr/298173", decoded_text)
            os.remove(cropped_image_path)

        with self.subTest("remote url"):
            pdf = "https://media3.neff-international.com/Documents/energylabel/en-IE/S187ZCX43G.pdf"
            img = small_pdf_2_image(pdf)
            cropped_image_path = energy_label_cropped_2_qr(img)
            decoded_text = read_qr(cropped_image_path)
            self.assertEqual('https://eprel.ec.europa.eu/qr/365228', decoded_text)
            os.remove(cropped_image_path)

    def test_extract_eprel_code_from_url(self):
        url = "https://eprel.ec.europa.eu/qr/298173"
        self.assertEqual("298173", extract_eprel_code_from_url(url))
        self.assertIsNone(extract_eprel_code_from_url("https://eprel.ec.europa.eu/qr/test"))
        self.assertIsNone(extract_eprel_code_from_url("https://eprel.ec.europa.eu/test/298173"))
        self.assertIsNone(extract_eprel_code_from_url("https://google.com/qr/298173"))
