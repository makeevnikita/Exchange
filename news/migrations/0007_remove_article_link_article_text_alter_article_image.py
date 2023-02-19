# Generated by Django 4.1.3 on 2023-02-03 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_alter_article_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='link',
        ),
        migrations.AddField(
            model_name='article',
            name='text',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='article',
            name='image',
            field=models.FileField(default='', upload_to='images/news/'),
        ),
    ]
