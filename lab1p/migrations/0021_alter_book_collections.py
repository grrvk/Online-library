# Generated by Django 4.1.6 on 2023-02-13 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab1p', '0020_alter_author_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='collections',
            field=models.ManyToManyField(blank=True, related_name='books_for_collecton', to='lab1p.collection'),
        ),
    ]