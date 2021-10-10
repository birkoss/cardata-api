from django.db import connection
from django.db.models import Q, Count, Case, When, IntegerField, Sum
from rest_framework import status, authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from birkoss.helpers import create_error_response
from dealers.models import Dealer, fetch_dealer

from .serializers import DealerSerializer


class dealers(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        dealers = Dealer.objects.all().order_by("name").annotate(
            cars_count=Count('dealers')
        ).annotate(
            makes_count=Count('dealers__model__make')
        ).annotate(
            active_cars_count=Count(
                Case(
                    When(
                        Q(dealers__date_removed=None, dealers__isnull=False),
                        then=1
                    ),
                    output_field=IntegerField(),
                )
            )
        ).annotate(
            sold_cars_count=Count(
                Case(
                    When(~Q(dealers__date_removed=None), then=1),
                    output_field=IntegerField(),
                )
            )
        )

        serializer = DealerSerializer(instance=dealers, many=True)

        return Response({
            'status': status.HTTP_200_OK,
            'dealers': serializer.data,
            'queries': len(connection.queries),
        }, status=status.HTTP_200_OK)


class dealer(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, dealer_id, format=None):
        dealer = fetch_dealer(id=dealer_id)
        if dealer is None:
            return create_error_response("Invalid dealer")

        serializer = DealerSerializer(
            instance=dealer,
            many=False
        )

        return Response({
            'status': status.HTTP_200_OK,
            'dealer': serializer.data
        }, status=status.HTTP_200_OK)


class stats_dealers(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        dealers = Dealer.objects.all()

        return Response({
            'status': status.HTTP_200_OK,
            'total': dealers.count()
        }, status=status.HTTP_200_OK)
