# Generated by Django 5.1.1 on 2024-11-11 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermodel',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
    ]