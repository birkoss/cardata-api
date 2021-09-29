from django.contrib import admin
from django.urls import path

from cars.api.urls import urlpatterns as cars_urlpatterns
from dealers.api.urls import urlpatterns as dealers_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
] + dealers_urlpatterns + cars_urlpatterns
