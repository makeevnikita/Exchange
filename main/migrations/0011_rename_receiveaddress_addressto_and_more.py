# Generated by Django 4.1.6 on 2023-03-12 21:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_rename_give_name_order_receive_name_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ReceiveAddress',
            new_name='AddressTo',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='give_address',
            new_name='address_to',
        ),
    ]