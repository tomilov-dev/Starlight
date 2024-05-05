# Generated by Django 5.0.2 on 2024-02-18 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0019_rename_moviegenres_moviegenre"),
    ]

    operations = [
        migrations.RenameField(
            model_name="imdb",
            old_name="kp_added",
            new_name="imdb_extra_added",
        ),
        migrations.AddField(
            model_name="imdb",
            name="image_url",
            field=models.URLField(
                blank=True, null=True, verbose_name="Ссылка на изображение"
            ),
        ),
        migrations.AlterField(
            model_name="collection",
            name="name_en",
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name="collection",
            name="name_ru",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name="imdb",
            name="slug",
            field=models.SlugField(max_length=250, unique=True, verbose_name="Slug"),
        ),
        migrations.AlterField(
            model_name="imdb",
            name="title_en",
            field=models.CharField(max_length=250, verbose_name="Название англ."),
        ),
        migrations.AlterField(
            model_name="imdb",
            name="title_ru",
            field=models.CharField(
                max_length=250, null=True, verbose_name="Название рус."
            ),
        ),
        migrations.AlterField(
            model_name="productioncompany",
            name="name",
            field=models.CharField(max_length=250),
        ),
    ]