# Generated by Django 5.0.2 on 2024-02-14 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0004_alter_imdb_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="genre",
            name="kp_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="genre",
            name="tmdb_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
