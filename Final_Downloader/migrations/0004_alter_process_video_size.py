# Generated by Django 4.0.5 on 2022-08-18 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Final_Downloader', '0003_alter_process_video_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='process',
            name='video_size',
            field=models.BigIntegerField(),
        ),
    ]