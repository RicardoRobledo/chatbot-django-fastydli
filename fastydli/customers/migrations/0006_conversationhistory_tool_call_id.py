# Generated by Django 5.1.3 on 2024-11-11 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0005_alter_conversationhistory_customer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversationhistory',
            name='tool_call_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]