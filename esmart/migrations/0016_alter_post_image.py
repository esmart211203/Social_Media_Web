# Generated by Django 4.2.5 on 2023-10-27 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esmart', '0015_post_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts'),
        ),
    ]
