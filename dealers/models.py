import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from birkoss.models import TimeStampedModel, UUIDModel


class Dealer(TimeStampedModel, UUIDModel, models.Model):
    name = models.CharField(max_length=100, default='')
    address = models.CharField(max_length=400, default='')
    city = models.CharField(max_length=200, default='')
    postal_code = models.CharField(max_length=6, default='')
    website = models.CharField(max_length=200, default='', blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0, blank=True)
    api_key = models.CharField(max_length=32, default='', blank=True, unique=True)
    feeds_url = models.TextField(blank=True)

    def __str__(self):
        return self.name


# Create an API token when an user is created
@receiver(post_save, sender=Dealer)
def create_api_key(sender, instance=None, created=False, **kwargs):
    if created:
        instance.api_key = uuid.uuid1().hex
        instance.save()


def fetch_dealer(**kwargs):
    try:
        dealer = Dealer.objects.filter(**kwargs).first()
    except ValidationError:
        return None

    return dealer
