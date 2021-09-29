from django.urls import path

from . import views as api_views


urlpatterns = [
    path(
        'api/dealers',
        api_views.dealers.as_view(),
        name='dealers'
    ),
    path(
        'api/dealer/<str:dealer_id>',
        api_views.dealer.as_view(),
        name='dealer'
    ),
    path(
        'api/dealer/<str:dealer_id>/cars',
        api_views.dealers.as_view(),
        name='cars'
    ),
    path(
        'api/car/<str:car_id>',
        api_views.dealer.as_view(),
        name='models'
    ),
]
