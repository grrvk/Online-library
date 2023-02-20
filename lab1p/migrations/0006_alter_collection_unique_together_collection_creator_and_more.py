# Generated by Django 4.1.6 on 2023-02-10 19:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lab1p', '0005_rename_useradded_collection_users_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='collection',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='collection',
            name='creator',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='collection',
            name='users',
        ),
    ]
