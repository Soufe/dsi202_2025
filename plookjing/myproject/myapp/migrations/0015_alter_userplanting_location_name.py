# Generated by Django 5.1.6 on 2025-05-30 23:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0014_remove_userplanting_location_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userplanting",
            name="location_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
