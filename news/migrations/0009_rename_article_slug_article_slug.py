# Generated by Django 4.1.3 on 2023-02-03 17:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0008_article_article_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='article_slug',
            new_name='slug',
        ),
    ]