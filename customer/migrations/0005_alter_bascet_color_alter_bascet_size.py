# Generated by Django 4.1.3 on 2022-12-09 08:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0002_review'),
        ('customer', '0004_bascet_color_bascet_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bascet',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerce.color'),
        ),
        migrations.AlterField(
            model_name='bascet',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerce.size'),
        ),
    ]
