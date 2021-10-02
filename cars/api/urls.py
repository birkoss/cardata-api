from django.urls import path

from . import views as api_views


urlpatterns = [
    path(
        'dealer/<str:dealer_id>/cars',
        api_views.cars.as_view(),
        name='cars'
    ),
    path(
        'dealer/<str:dealer_id>/cars/active',
        api_views.cars_active.as_view(),
        name='cars-active'
    ),
    path(
        'car/<str:car_id>',
        api_views.car.as_view(),
        name='car'
    ),
    path(
        'stats/cars',
        api_views.stats_cars.as_view(),
        name='stats-cars'
    ),
    path(
        'makes',
        api_views.makes.as_view(),
        name='makes'
    ),
    path(
        'make/<str:make_id>/models',
        api_views.models.as_view(),
        name='makes-models'
    ),
]
