# Generated by Django 5.0.2 on 2024-02-15 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0015_alter_collection_options_alter_country_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productioncompany",
            name="country",
            field=models.CharField(max_length=200),
        ),
    ]
