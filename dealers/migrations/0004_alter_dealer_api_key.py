# Generated by Django 3.2.7 on 2021-09-29 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dealers', '0003_alter_dealer_api_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dealer',
            name='api_key',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
    ]
