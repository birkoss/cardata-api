from django.db import models

from birkoss.models import TimeStampedModel, UUIDModel


class Make(TimeStampedModel, UUIDModel, models.Model):
    name = models.CharField(max_length=100, default='')


class Model(TimeStampedModel, UUIDModel, models.Model):
    name = models.CharField(max_length=100, default='')

    make = models.ForeignKey(
        'Make',
        on_delete=models.PROTECT,
        null=True,
        related_name="models"
    )
