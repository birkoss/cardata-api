# Generated by Django 3.2.7 on 2021-09-30 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dealers', '0008_alter_dealer_api_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='dealer',
            name='feeds_url',
            field=models.TextField(blank=True),
        ),
    ]
