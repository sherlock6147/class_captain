# Generated by Django 4.2.6 on 2023-10-25 12:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0002_secrettoken"),
    ]

    operations = [
        migrations.AlterField(
            model_name="secrettoken",
            name="code",
            field=models.CharField(default="29e732", max_length=6),
        ),
    ]
