# Generated by Django 3.2.7 on 2021-10-05 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0007_carhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='sold_days_count',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
