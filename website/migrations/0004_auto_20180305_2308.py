# Generated by Django 2.0.2 on 2018-03-05 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_song_is_favorite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='album_title',
            field=models.CharField(max_length=500),
        ),
    ]