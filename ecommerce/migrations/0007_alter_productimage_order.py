# Generated by Django 4.1.3 on 2022-12-12 07:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0006_alter_productimage_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='order',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
