# Generated by Django 2.0.2 on 2018-03-06 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_auto_20180306_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='movie_picture',
            field=models.FileField(upload_to='media/'),
        ),
    ]
