# Generated by Django 5.1.6 on 2025-05-28 12:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0006_tree_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tree",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="tree/"),
        ),
    ]
