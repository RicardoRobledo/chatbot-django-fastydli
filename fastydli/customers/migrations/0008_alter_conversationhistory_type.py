# Generated by Django 5.1.3 on 2024-11-12 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0007_conversationhistory_tool_calls_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversationhistory',
            name='type',
            field=models.CharField(blank=True, default='message', max_length=30, null=True),
        ),
    ]