# Generated by Django 3.2.7 on 2021-10-02 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0005_alter_car_date_removed'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='model',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='car',
            name='trim',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
