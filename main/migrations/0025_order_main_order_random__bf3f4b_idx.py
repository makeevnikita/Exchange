# Generated by Django 4.1.6 on 2023-05-01 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_alter_order_order_with_respect_to'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['random_string'], name='main_order_random__bf3f4b_idx'),
        ),
    ]
