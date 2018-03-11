# Generated by Django 2.0.2 on 2018-03-08 08:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('website', '0014_auto_20180308_0527'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subtotal', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('cart_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='ticket',
            name='price',
            field=models.DecimalField(decimal_places=2, default=5.5, max_digits=10),
        ),
        migrations.AddField(
            model_name='ticket',
            name='cart',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='website.ShoppingCart'),
        ),
    ]
