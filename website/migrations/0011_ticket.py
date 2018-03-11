# Generated by Django 2.0.2 on 2018-03-07 03:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_auto_20180306_2321'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=4)),
                ('row', models.IntegerField()),
                ('seat', models.CharField(max_length=1)),
                ('available', models.BooleanField(default=True)),
                ('showtime', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.ShowTime')),
            ],
        ),
    ]