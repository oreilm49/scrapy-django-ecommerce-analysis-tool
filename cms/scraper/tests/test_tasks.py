from django.test import TestCase
from model_mommy import mommy

from cms.models import Product, ProductAttribute, Category, EprelCategory
from cms.scraper.tasks import crawl_eprel_data


class TestTasks(TestCase):

    def test_crawl_eprel_data(self):
        category: Category = mommy.make(Category, name="washing machines")
        eprel_category: EprelCategory = mommy.make(EprelCategory, category=category, name="washingmachines2019")
        product: Product = Product.objects.create(model="FFB 8448 WV UK", category=category, eprel_category=eprel_category, eprel_code="258076")

        with self.subTest("nothing scraped"):
            product.eprel_scraped = True
            product.save()
            crawl_eprel_data()
            self.assertFalse(ProductAttribute.objects.filter(product=product).exists())

        with self.subTest("data scraped"):
            product.eprel_scraped = False
            product.save()
            crawl_eprel_data()
            self.assertTrue(ProductAttribute.objects.filter(product=product).exists())
            product: Product = Product.objects.get(pk=product.pk)
            self.assertTrue(product.eprel_scraped)
