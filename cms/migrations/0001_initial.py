# Generated by Django 3.1.5 on 2021-02-22 15:59

import cms.models
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('alternate_names', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), blank=True, default=list, null=True, size=None, verbose_name='Alternate names')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('alternate_names', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), blank=True, default=list, null=True, size=None, verbose_name='Alternate names')),
                ('parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sub_categories', to='cms.category', verbose_name='Parent')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('model', models.CharField(max_length=100, unique=True, verbose_name='Model')),
                ('alternate_models', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), blank=True, default=list, null=True, size=None, verbose_name='Alternate models')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cms.category', verbose_name='Category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('name', models.CharField(help_text='The unit name', max_length=100, unique=True, verbose_name='Name')),
                ('alternate_names', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), blank=True, default=list, null=True, size=None, verbose_name='Alternate names')),
                ('widget', models.CharField(choices=[('django.forms.widgets.TextInput', 'Text'), ('django.forms.widgets.NumberInput', 'Number (integer)'), ('cms.form_widgets.FloatInput', 'Number (decimal)'), ('django.forms.widgets.CheckboxInput', 'Checkbox'), ('django.forms.widgets.DateTimeInput', 'Date & Time')], help_text="The input widget, which denotes the data type, serializer and deserializer of the unit's corresponding values.", max_length=70, verbose_name='widget')),
                ('repeat', models.CharField(blank=True, choices=[('once', 'Once'), ('hourly', 'Hourly'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='once', help_text='The frequency with which this unit should be tracked.', max_length=100, null=True, verbose_name='Repeat')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('name', models.CharField(help_text='The website name', max_length=100, unique=True, verbose_name='Name')),
                ('domain', models.CharField(help_text='The website domain name', max_length=100, unique=True, verbose_name='Domain')),
                ('currency', models.ForeignKey(blank=True, help_text='The currency this website trades in.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='websites', to='cms.unit', verbose_name='Currency')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WebsiteProductAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('data', models.JSONField(default=cms.models.json_data_default, help_text='The data for this attribute', null=True, verbose_name='Data')),
                ('attribute_type', models.ForeignKey(blank=True, help_text='The data type for this attribute', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='websiteproductattributes', to='cms.attributetype', verbose_name='Data type')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='websiteproductattributes', to='cms.product', verbose_name='Product')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productattributes', to='cms.website', verbose_name='Website')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('url', models.CharField(help_text='The page url', max_length=100, unique=True, verbose_name='Url')),
                ('url_type', models.CharField(choices=[('category', 'Category'), ('product', 'Product')], max_length=100, verbose_name='Type')),
                ('last_scanned', models.DateTimeField(blank=True, null=True, verbose_name='Last scanned')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='urls', to='cms.category')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urls', to='cms.website')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Selector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('selector_type', models.CharField(choices=[('model', 'Model'), ('price', 'Price'), ('text', 'Text'), ('table', 'Table'), ('image', 'Image'), ('link', 'Link'), ('pagination', 'Pagination'), ('table_value_column', 'Table Value Column'), ('table_label_column', 'Table Label Column')], max_length=100, verbose_name='Type')),
                ('css_selector', models.CharField(help_text='The CSS selector used to find page data.', max_length=100, verbose_name='CSS Selector')),
                ('regex', models.CharField(blank=True, help_text='A regular expression used to extract data', max_length=100, null=True, verbose_name='Regular Expression')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sub_selectors', to='cms.selector', verbose_name='Parent')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selectors', to='cms.website')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('image_type', models.CharField(choices=[('main', 'Main'), ('thumbnail', 'Thumbnail')], max_length=100, verbose_name='Type')),
                ('image', models.FilePathField(verbose_name='image')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='cms.product', verbose_name='Product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='attributetype',
            name='unit',
            field=models.ForeignKey(blank=True, help_text='The data type for this attribute', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attribute_types', to='cms.unit', verbose_name='Data type'),
        ),
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('data', models.JSONField(default=cms.models.json_data_default, help_text='The data for this attribute', null=True, verbose_name='Data')),
                ('attribute_type', models.ForeignKey(blank=True, help_text='The data type for this attribute', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='productattributes', to='cms.attributetype', verbose_name='Data type')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productattributes', to='cms.product', verbose_name='Product')),
            ],
            options={
                'unique_together': {('product', 'attribute_type')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='attributetype',
            unique_together={('name', 'unit')},
        ),
    ]
