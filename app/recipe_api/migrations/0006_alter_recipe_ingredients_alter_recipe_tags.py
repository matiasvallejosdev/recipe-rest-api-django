# Generated by Django 4.0 on 2023-01-15 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_api', '0005_ingredient_recipe_ingredients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(blank=True, to='recipe_api.Ingredient'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(blank=True, to='recipe_api.Tag'),
        ),
    ]
