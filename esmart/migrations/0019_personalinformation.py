# Generated by Django 4.2.5 on 2023-10-30 16:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('esmart', '0018_province_page'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sex', models.CharField(choices=[('male', 'Trai'), ('female', 'Gái'), ('3rd_gender', 'Giới tính thứ 3'), ('hidden', 'Không tiết lộ')], max_length=50, null=True)),
                ('relationship', models.CharField(choices=[('single', 'Độc thân'), ('dating', 'Hẹn hò')], max_length=50, null=True)),
                ('degree', models.CharField(choices=[('none', 'Không có'), ('college', 'Cao đẳng'), ('university', 'Đại học')], max_length=50, null=True)),
                ('home_town', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='home_town', to='esmart.province')),
                ('residence', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='residence', to='esmart.province')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('workplace', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='page', to='esmart.page')),
            ],
        ),
    ]
