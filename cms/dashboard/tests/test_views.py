from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy

from cms.dashboard.forms import CategoryTableForm
from cms.dashboard.models import CategoryTable
from cms.models import AttributeType, Category


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
            response: TemplateResponse = self.client.get(reverse('dashboard:category-tables'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "No category tables")
            self.assertContains(response, "New")

        with self.subTest("tables"):
            mommy.make(CategoryTable, name="test 1")
            mommy.make(CategoryTable, name="test 2")
            response: TemplateResponse = self.client.get(reverse('dashboard:category-tables'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "test 1")
            self.assertContains(response, "test 2")

    def test_category_table_create(self):
        with self.subTest("page content"):
            response: TemplateResponse = self.client.get(reverse('dashboard:category-table-create'))
            self.assertIsInstance(response.context_data['form'], CategoryTableForm)
            self.assertContains(response, 'Create New Category Table')

        with self.subTest("post"):
            response: TemplateResponse = self.client.post(reverse('dashboard:category-table-create'), data={
                'name': 'test table',
                'x_axis_attribute': mommy.make(AttributeType, name="x axis attr").pk,
                'x_axis_values': '1, 2, 3',
                'y_axis_attribute': mommy.make(AttributeType, name="y axis attr").pk,
                'y_axis_values': '4, 5, 6',
                'category': mommy.make(Category, name="washing").pk,
                'query': 'test query',
            }, follow=True)
            self.assertEqual(response.status_code, 200)
            table: CategoryTable = CategoryTable.objects.first()
            self.assertRedirects(response, reverse('dashboard:category-table', kwargs={'pk': table.pk}))
            self.assertContains(response, 'test table')
            self.assertContains(response, 'Successfully created &quot;test table&quot;')

    def test_category_table_update(self):
        table: CategoryTable = mommy.make(CategoryTable, name="test table")
        url: str = reverse('dashboard:category-table-update', kwargs={'pk': table.pk})
        with self.subTest("page content"):
            response: TemplateResponse = self.client.get(url)
            self.assertIsInstance(response.context_data['form'], CategoryTableForm)
            self.assertContains(response, 'Edit test table')

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
            self.assertEqual(response.status_code, 200)
            self.assertRedirects(response, reverse('dashboard:category-table', kwargs={'pk': table.pk}))
            self.assertNotContains(response, 'test table')
            self.assertContains(response, 'Successfully updated &quot;modified table name&quot;')

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
            self.assertEqual(response.status_code, 200)
            self.assertRedirects(response, reverse('dashboard:category-tables'))
            self.assertContains(response, 'Successfully deleted &quot;modified table name&quot;')
            table: CategoryTable = CategoryTable.objects.get(pk=table.pk)
            self.assertFalse(table.publish)
