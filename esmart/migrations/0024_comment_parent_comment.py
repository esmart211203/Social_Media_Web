# Generated by Django 4.2.5 on 2023-11-14 22:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('esmart', '0023_favorites_receiver_alter_favorites_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='parent_comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='esmart.comment'),
        ),
    ]