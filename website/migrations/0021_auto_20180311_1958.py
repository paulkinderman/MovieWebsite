# Generated by Django 2.0.2 on 2018-03-11 19:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0020_order_total_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='total_price',
            new_name='order_price',
        ),
    ]