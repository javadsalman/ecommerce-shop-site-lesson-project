# Generated by Django 4.1.3 on 2023-01-04 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0012_alter_product_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='comment',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
