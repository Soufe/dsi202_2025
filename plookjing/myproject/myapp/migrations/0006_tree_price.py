# Generated by Django 5.1.6 on 2025-05-28 12:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0005_equipmentorder_plantingplan_treecare_usertree_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tree",
            name="price",
            field=models.DecimalField(decimal_places=2, default=100, max_digits=10),
            preserve_default=False,
        ),
    ]
