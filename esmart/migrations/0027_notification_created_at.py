# Generated by Django 4.2.5 on 2023-11-18 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esmart', '0026_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
