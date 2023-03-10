# Generated by Django 4.1.3 on 2023-02-25 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='give_sum',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=6),
        ),
        migrations.AlterField(
            model_name='order',
            name='receive_sum',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=6),
        ),
    ]
