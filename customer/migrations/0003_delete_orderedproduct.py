# Generated by Django 4.1.3 on 2022-12-09 08:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_order_wishlist_orderedproduct_bascet'),
    ]

    operations = [
        migrations.DeleteModel(
            name='OrderedProduct',
        ),
    ]
