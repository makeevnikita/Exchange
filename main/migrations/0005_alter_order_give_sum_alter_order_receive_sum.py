# Generated by Django 4.1.3 on 2023-02-25 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_order_give_sum_alter_order_receive_sum'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='give_sum',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='receive_sum',
            field=models.FloatField(default=0),
        ),
    ]
