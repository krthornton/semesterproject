# Generated by Django 2.2.5 on 2019-10-19 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_item_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='slug',
            field=models.SlugField(default=object, unique=True),
            preserve_default=False,
        ),
    ]
