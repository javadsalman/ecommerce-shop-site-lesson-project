# Generated by Django 4.1.3 on 2023-01-13 09:07

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0019_passwordreset_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordreset',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True),
        ),
    ]
