# Generated by Django 5.1.1 on 2024-09-28 20:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_conversationhistory_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customermodel',
            name='address',
        ),
    ]
