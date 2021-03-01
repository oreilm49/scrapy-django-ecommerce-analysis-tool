from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy

from dashboard.forms import CategoryTableForm
from dashboard.models import CategoryTable
from models import AttributeType, Category


class TestViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user: User = User.objects.create_user('testuser', password='password')

    def setUp(self) -> None:
        super().setUp()
        self.client.force_login(self.user)

    def test_category_tables(self):
        with self.subTest("empty"):
            response: TemplateResponse = self.client.get(reverse('category-tables'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "No category tables")
            self.assertContains(response, "Create")

        with self.subTest("tables"):
            mommy.make(CategoryTable, name="test 1")
            mommy.make(CategoryTable, name="test 2")
            response: TemplateResponse = self.client.get(reverse('category-tables'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "test 1")
            self.assertContains(response, "test 2")

    def test_category_table_create(self):
        with self.subTest("page content"):
            response: TemplateResponse = self.client.get(reverse('category-table-create'))
            self.assertContains(response, CategoryTableForm)
            self.assertContains(response, 'Create New Category Table')

        with self.subTest("post"):
            response: TemplateResponse = self.client.post(reverse('category-table-create'), data={
                'name': 'test table',
                'x_axis_attribute': mommy.make(AttributeType, name="x axis attr").pk,
                'x_axis_values': '1, 2, 3',
                'y_axis_attribute': mommy.make(AttributeType, name="y axis attr").pk,
                'y_axis_values': '4, 5, 6',
                'category': mommy.make(Category, name="washing").pk,
                'query': 'test query',
            }, follow=True)
            self.assertEqual(response.status_code, 201)
            self.assertRedirects(response, reverse('category-tables'))
            self.assertContains(response, 'test table')
            self.assertContains(response, 'Sucessfully created "test table"')

    def test_category_table_update(self):
        table: CategoryTable = mommy.make(CategoryTable, name="test table")
        url: str = reverse('category-table-update', kwargs={'pk': table.pk})
        with self.subTest("page content"):
            response: TemplateResponse = self.client.get(url)
            self.assertContains(response, CategoryTableForm)
            self.assertContains(response, 'Update test table')

        with self.subTest("post"):
            response: TemplateResponse = self.client.post(url, data={
                'name': 'modified table name',
                'x_axis_attribute': mommy.make(AttributeType, name="x axis attr").pk,
                'x_axis_values': '1, 2, 3',
                'y_axis_attribute': mommy.make(AttributeType, name="y axis attr").pk,
                'y_axis_values': '4, 5, 6',
                'category': mommy.make(Category, name="washing").pk,
                'query': 'test query',
            }, follow=True)
            self.assertEqual(response.status_code, 201)
            self.assertRedirects(response, reverse('category-tables'))
            self.assertContains(response, 'test table')
            self.assertContains(response, 'Sucessfully updated "modified table name"')

        with self.subTest("table content"):
            table: CategoryTable = CategoryTable.objects.get(pk=table.pk)
            self.assertEqual(table.name, 'modified table name')
            self.assertEqual(table.x_axis_attribute.name, 'x axis attr')
            self.assertEqual(table.x_axis_values, ['1', '2', '3'])
            self.assertEqual(table.y_axis_attribute.name, 'y axis attr')
            self.assertEqual(table.y_axis_values, ['4', '5', '6'])
            self.assertEqual(table.category.name, 'washing')
            self.assertEqual(table.query, 'test query')

        with self.subTest("delete"):
            response: TemplateResponse = self.client.post(url, data={'delete': 'save'}, follow=True)
            self.assertEqual(response.status_code, 201)
            self.assertRedirects(response, reverse('category-tables'))
            self.assertContains(response, 'Sucessfully deleted "modified table name"')
            table: CategoryTable = CategoryTable.objects.get(pk=table.pk)
            self.assertFalse(table.publish)
