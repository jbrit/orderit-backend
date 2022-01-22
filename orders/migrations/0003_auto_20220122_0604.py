# Generated by Django 3.2.7 on 2022-01-22 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20220122_0538'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.ImageField(null=True, upload_to='items'),
        ),
        migrations.AddField(
            model_name='meal',
            name='images',
            field=models.ImageField(null=True, upload_to='meals'),
        ),
    ]