# Generated by Django 4.0.5 on 2022-08-18 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Final_Downloader', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='video_size',
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
    ]
