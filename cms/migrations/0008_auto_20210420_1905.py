# Generated by Django 3.1.5 on 2021-04-20 19:05

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0007_auto_20210420_0705'),
    ]

    operations = [
        migrations.AddField(
            model_name='website',
            name='website_type',
            field=models.CharField(choices=[('retailer', 'Retailer'), ('supplier', 'Supplier')], default='retailer', max_length=100, verbose_name='Type'),
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='order')),
                ('publish', models.BooleanField(default=True, verbose_name='publish')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Autogenerated unique id for this item in database', verbose_name='unique id')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modification time')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('image', models.ImageField(blank=True, null=True, upload_to='brand_images/', verbose_name='image')),
                ('website', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='brands', to='cms.website')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='cms.brand', verbose_name='Brand'),
        ),
    ]