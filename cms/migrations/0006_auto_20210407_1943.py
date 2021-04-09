# Generated by Django 3.1.5 on 2021-04-07 19:43

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0005_categoryattributeconfig_scoring'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selector',
            name='selector_type',
            field=models.CharField(choices=[('model', 'Model'), ('price', 'Price'), ('text', 'Text'), ('table', 'Table'), ('image', 'Image'), ('energy_label_pdf', 'Energy Label PDF'), ('link', 'Link'), ('pagination', 'Pagination'), ('table_value_column', 'Table Value Column'), ('table_value_column_bool', 'Table Value Column Bool'), ('table_label_column', 'Table Label Column')], max_length=100, verbose_name='Type'),
        ),
        migrations.CreateModel(
            name='ProductFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('file_type', models.CharField(choices=[('energy_label_pdf', 'Energy Label PDF')], max_length=100, verbose_name='Type')),
                ('file', models.FileField(upload_to='product_files/', verbose_name='file')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='cms.product', verbose_name='Product')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]