from django.urls import path

from . import views as api_views


urlpatterns = [
    path(
        'dealers',
        api_views.dealers.as_view(),
        name='dealers'
    ),
    path(
        'dealer/<str:dealer_id>',
        api_views.dealer.as_view(),
        name='dealer'
    ),
    path(
        'dealers/cars',
        api_views.stats_dealers.as_view(),
        name='dealers-cars'
    )
]
