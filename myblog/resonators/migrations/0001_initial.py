# Generated by Django 5.2.1 on 2025-05-25 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('rarity', models.CharField(max_length=10)),
                ('weapon', models.CharField(max_length=50)),
                ('affiliation', models.CharField(max_length=100)),
                ('birthday', models.CharField(max_length=20)),
                ('birthplace', models.CharField(max_length=100)),
                ('attribute', models.CharField(max_length=50)),
                ('role', models.CharField(max_length=100)),
                ('hp', models.PositiveIntegerField()),
                ('atk', models.PositiveIntegerField()),
                ('defense', models.PositiveIntegerField()),
            ],
        ),
    ]
