# Generated by Django 3.1.5 on 2021-04-10 13:52

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0005_categoryattributeconfig_scoring'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='eprel_code',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='EPREL Code'),
        ),
        migrations.AddField(
            model_name='product',
            name='eprel_scraped',
            field=models.BooleanField(default=False, help_text='Has the EPREL database been scraped for this product?', verbose_name='EPREL Scraped'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image_type',
            field=models.CharField(choices=[('main', 'Main'), ('thumbnail', 'Thumbnail'), ('energy_label_img', 'Energy Label'), ('energy_label_qr', 'Energy Label QR')], max_length=100, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='selector',
            name='selector_type',
            field=models.CharField(choices=[('model', 'Model'), ('price', 'Price'), ('text', 'Text'), ('table', 'Table'), ('image', 'Image'), ('energy_label_pdf', 'Energy Label PDF'), ('link', 'Link'), ('pagination', 'Pagination'), ('table_value_column', 'Table Value Column'), ('table_value_column_bool', 'Table Value Column Bool'), ('table_label_column', 'Table Label Column')], max_length=100, verbose_name='Type'),
        ),
        migrations.CreateModel(
            name='EprelCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('name', models.CharField(max_length=100, verbose_name='category name')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='eprel_names', to='cms.category')),
            ],
            options={
                'unique_together': {('category', 'name')},
            },
        ),
        migrations.AddField(
            model_name='product',
            name='eprel_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cms.eprelcategory', verbose_name='EPREL Category'),
        ),
    ]