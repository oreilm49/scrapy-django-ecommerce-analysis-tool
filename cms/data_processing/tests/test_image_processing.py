import shutil

import requests
from django.test import TestCase

from cms.data_processing.image_processing import small_pdf_2_image
from cms.scraper.settings import IMAGES_ENERGY_LABELS_STORE


class TestUnits(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(IMAGES_ENERGY_LABELS_STORE)
        super().tearDownClass()

    def test_small_pdf_2_image(self):
        pdf_url = "https://cc.isitetv.com/clients/wp/whirlpool/859991530490/documentation/eur/whirlpool-fwl71253wuk-energy-label-el859991530490.pdf"
        with self.subTest("url valid"):
            self.assertEqual(requests.get(pdf_url).status_code, 200)

        with self.subTest("valid pdf"):
            image_path = small_pdf_2_image(pdf_url)
            self.assertIn(IMAGES_ENERGY_LABELS_STORE, image_path)
            self.assertIn('.png', image_path)
            open(image_path)

        with self.subTest("pdf file validation"):
            with self.assertRaises(Exception) as context:
                small_pdf_2_image("test.jpg")
            self.assertEqual(str(context.exception), "Download url is not a pdf link: 'test.jpg'")
