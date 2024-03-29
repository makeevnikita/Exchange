# Generated by Django 4.1.6 on 2023-03-12 21:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_order_paid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='give_name',
            new_name='receive_name',
        ),
        migrations.AlterField(
            model_name='order',
            name='give_address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.receiveaddress'),
        ),
        migrations.AlterField(
            model_name='order',
            name='receive_address',
            field=models.CharField(default='Без адреса', max_length=255),
        ),
    ]
