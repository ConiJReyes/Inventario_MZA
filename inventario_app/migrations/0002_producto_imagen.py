# Generated by Django 5.2 on 2025-05-20 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='productos/'),
        ),
    ]
