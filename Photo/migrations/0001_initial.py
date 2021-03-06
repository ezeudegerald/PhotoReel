# Generated by Django 2.0.5 on 2018-05-19 21:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=250)),
                ('reset_hash', models.CharField(max_length=250)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('expires_on', models.DateTimeField(blank=True, null=True)),
                ('is_used', models.BooleanField(default=0)),
                ('used_on', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=0)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'PasswordReset',
                'verbose_name_plural': 'PasswordResets',
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=150, null=True)),
                ('description', models.TextField(default='')),
                ('image_url', models.ImageField(blank=True, default='No.jpg', null=True, upload_to='photo/%Y/%m/%d')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('location', models.CharField(default='unknown', max_length=150)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Photo',
                'verbose_name_plural': 'Photos',
            },
        ),
    ]
