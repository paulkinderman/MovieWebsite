# Generated by Django 2.0.2 on 2018-03-08 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_auto_20180308_0841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='type',
            field=models.CharField(default='NA', max_length=2),
        ),
    ]