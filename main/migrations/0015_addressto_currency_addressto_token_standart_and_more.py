# Generated by Django 4.1.6 on 2023-03-26 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_remove_receivecurrency_address_addresstoreceive'),
    ]

    operations = [
        migrations.AddField(
            model_name='addressto',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.receivecurrency'),
        ),
        migrations.AddField(
            model_name='addressto',
            name='token_standart',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.tokenstandart'),
        ),
        migrations.DeleteModel(
            name='AddressToReceive',
        ),
    ]