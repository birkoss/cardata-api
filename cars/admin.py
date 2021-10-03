from django.contrib import admin

from .models import Make, Model, Car, CarHistory


admin.site.register(Make)
admin.site.register(Model)
admin.site.register(Car)
admin.site.register(CarHistory)
