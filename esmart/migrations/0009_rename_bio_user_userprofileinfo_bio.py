# Generated by Django 4.2.5 on 2023-10-25 08:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('esmart', '0008_userprofileinfo_bio_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofileinfo',
            old_name='bio_user',
            new_name='bio',
        ),
    ]