# Generated by Django 5.0.2 on 2024-02-16 09:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0018_remove_genre_kp_name_genre_name_ru"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="MovieGenres",
            new_name="MovieGenre",
        ),
    ]
