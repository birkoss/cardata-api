from django.urls import path

from . import views as api_views


urlpatterns = [
    path(
        'dealer/<str:dealer_id>/cars',
        api_views.dealer_cars.as_view(),
        name='dealer-cars'
    ),
    path(
        'dealer/<str:dealer_id>/cars/active',
        api_views.cars_active.as_view(),
        name='cars-active'
    ),
    path(
        'cars',
        api_views.cars.as_view(),
        name='cars'
    ),
    path(
        'export',
        api_views.export.as_view(),
        name='export'
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
        'stats/weekly-cars',
        api_views.stats_weekly_cars.as_view(),
        name='stats-weekly-cars'
    ),
    path(
        'makes',
        api_views.makes.as_view(),
        name='makes'
    ),
    path(
        'models',
        api_views.models.as_view(),
        name='models'
    ),
    path(
        'make/<str:make_id>/models',
        api_views.models.as_view(),
        name='makes-models'
    ),
    path(
        'histories',
        api_views.histories.as_view(),
        name='histories'
    ),
    path(
        'sales',
        api_views.sales.as_view(),
        name='sales'
    ),
]
