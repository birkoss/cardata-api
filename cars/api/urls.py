from django.urls import path

from . import views as api_views


urlpatterns = [
    path(
        'api/dealer/<str:dealer_id>/cars',
        api_views.cars.as_view(),
        name='cars'
    ),
    path(
        'api/car/<str:car_id>',
        api_views.car.as_view(),
        name='car'
    ),
]
