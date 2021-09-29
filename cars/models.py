from django.db import models
from django.core.exceptions import ValidationError

from birkoss.models import TimeStampedModel, UUIDModel


class Make(TimeStampedModel, UUIDModel, models.Model):
    name = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.name


class Model(TimeStampedModel, UUIDModel, models.Model):
    make = models.ForeignKey(
        'Make',
        on_delete=models.PROTECT,
        null=True,
        related_name="models"
    )

    name = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.make.name + " " + self.name


class Car(TimeStampedModel, UUIDModel, models.Model):
    model = models.ForeignKey(
        'Model',
        on_delete=models.PROTECT,
        null=True,
        related_name="cars"
    )

    trim = models.CharField(max_length=100, default='')
    year = models.CharField(max_length=6, default='')
    dealer = models.ForeignKey(
        'dealers.Dealer',
        on_delete=models.PROTECT,
        null=True,
        related_name="dealers"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)

    vin = models.CharField(max_length=20, default='')

    date_removed = models.DateTimeField(blank=True, null=True)

    mileage = models.IntegerField(default=0, blank=True)
    images_count = models.IntegerField(default=0, blank=True)

    class CarCondition(models.TextChoices):
        USED = 'used', 'Used'
        NEW = 'new', 'New'

    condition = models.CharField(
        max_length=4,
        choices=CarCondition.choices,
        default=CarCondition.USED,
    )

    raw_exterior_color = models.CharField(max_length=100, default='', blank=True)
    raw_interior_color = models.CharField(max_length=100, default='', blank=True)
    raw_body_style = models.CharField(max_length=100, default='', blank=True)
    raw_transmission = models.CharField(max_length=100, default='', blank=True)
    raw_fuel_type = models.CharField(max_length=100, default='', blank=True)
    raw_drivetrain = models.CharField(max_length=100, default='', blank=True)

    def __str__(self):
        return self.model.__str__() + " " + self.trim + " " + self.year


def fetch_car(**kwargs):
    try:
        car = Car.objects.filter(**kwargs).first()
    except ValidationError:
        return None

    return car