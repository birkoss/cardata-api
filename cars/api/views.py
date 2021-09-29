from rest_framework import status, authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from birkoss.helpers import create_error_response
from dealers.models import Dealer, fetch_dealer
from cars.models import Car, fetch_car

from .serializers import CarSerializer


class cars(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, dealer_id, format=None):
        dealer = fetch_dealer(id=dealer_id)
        if dealer is None:
            return create_error_response("Invalid dealer")

        cars = Car.objects.filter(dealer=dealer).order_by("trim")

        serializer = CarSerializer(instance=cars, many=True)

        return Response({
            'status': status.HTTP_200_OK,
            'dealers': serializer.data
        }, status=status.HTTP_200_OK)


class car(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, car_id, format=None):
        car = fetch_car(id=car_id)
        if car is None:
            return create_error_response("Invalid car")

        serializer = CarSerializer(
            instance=car,
            many=False
        )

        return Response({
            'status': status.HTTP_200_OK,
            'car': serializer.data
        }, status=status.HTTP_200_OK)
