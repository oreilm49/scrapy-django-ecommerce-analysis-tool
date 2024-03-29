# Generated by Django 3.1.5 on 2021-03-07 14:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('name', models.CharField(help_text='The name for this dashboard', max_length=100, verbose_name='Name')),
                ('x_axis_values', models.JSONField(default=list, help_text='The values products must have for the x axis attribute in order to appear in the table.', verbose_name='X Axis Values')),
                ('y_axis_values', models.JSONField(default=list, help_text='The values products must have for the y axis attribute in order to appear in the table.', verbose_name='Y Axis Values')),
                ('query', models.CharField(blank=True, help_text='General search text used to further filter products.', max_length=100, null=True, verbose_name='Search')),
                ('category', models.ForeignKey(help_text='The category products should belong to in order to appear in the table.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='cms.category', verbose_name='Category')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='User')),
                ('x_axis_attribute', models.ForeignKey(help_text='The attribute used to group products into rows on the table.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category_tables_x_axis', to='cms.attributetype', verbose_name='X Axis Attribute')),
                ('y_axis_attribute', models.ForeignKey(help_text='The attribute used to group products into rows on the table.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category_tables_y_axis', to='cms.attributetype', verbose_name='Y Axis Attribute')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
