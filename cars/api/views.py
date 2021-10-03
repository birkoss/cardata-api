from datetime import datetime

from django.db import connection
from django.db.models import Q, Count
from rest_framework import status, authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from birkoss.helpers import create_error_response, validate_date
from dealers.models import fetch_dealer
from cars.models import Car, Make, Model, fetch_car, fetch_make, fetch_model

from .serializers import CarSerializer, CarWriteSerializer, MakeSerializer, ModelSerializer  # nopep8


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
            'cars': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, dealer_id, format=None):
        dealer = fetch_dealer(id=dealer_id)
        if dealer is None:
            return create_error_response("Invalid dealer")

        if "make" not in request.data:
            return create_error_response("Missing make")
        if "model" not in request.data:
            return create_error_response("Missing model")
        if "vin" not in request.data:
            return create_error_response("Missing VIN")

        data = request.data.copy()

        # @TODO: Better handling, also use an associated table to prevent human errors and duplicates  # nopep8
        data['make'] = data['make'].strip()
        data['model'] = data['model'].strip()

        if "special_price" in data and data['special_price'] == "":
            data['special_price'] = 0

        # Active car with the same VIN
        car = fetch_car(
            dealer=dealer,
            vin__iexact=request.data['vin'].lower(),
            date_removed=None
        )
        if car is not None:
            return create_error_response("This dealer already own a car with this VIN")  # nopep8

        make = fetch_make(name__iexact=request.data['make'].lower())
        if make is None:
            make = Make(name=request.data['make'])
            make.save()

        model = fetch_model(
            name__iexact=request.data['model'].lower(),
            make=make
        )
        if model is None:
            model = Model(
                name=request.data['model'],
                make=make
            )
            model.save()

        # Edge case, a car was REMOVED from inventory, and added back
        car = fetch_car(
            dealer=dealer,
            vin__iexact=request.data['vin'].lower(),
        )
        if car is not None:
            car.date_removed = None
            car.save()
            return Response({
                'status': status.HTTP_200_OK,
            })

        serializer = CarWriteSerializer(data=data)

        if serializer.is_valid():
            serializer.save(
                dealer=dealer,
                model=model
            )

            return Response({
                'status': status.HTTP_200_OK,
            })
        else:
            # @TODO: Use serializer.errors
            print(serializer.errors)
            return create_error_response(serializer.error_messages)


class cars_active(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, dealer_id, format=None):
        dealer = fetch_dealer(id=dealer_id)
        if dealer is None:
            return create_error_response("Invalid dealer")

        cars = Car.objects.filter(
            dealer=dealer,
            date_removed=None
        ).order_by("trim")

        serializer = CarSerializer(instance=cars, many=True)

        return Response({
            'status': status.HTTP_200_OK,
            'cars': serializer.data
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

    def delete(self, request, car_id, format=None):
        car = fetch_car(id=car_id)
        if car is None:
            return create_error_response("Invalid car")

        car.date_removed = datetime.now()
        car.save()

        return Response({
            'status': status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class stats_cars(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):

        filters = Q()

        _condition = request.GET.get("condition", "")
        if _condition == "used" or _condition == "new":
            filters.add(Q(condition=_condition), Q.AND)

        _status = request.GET.get("status", "")
        if _status == "available":
            filters.add(Q(date_removed=None), Q.AND)
        elif _status == "sold":
            filters.add(~Q(date_removed=None), Q.AND)

        _date_from = request.GET.get("date-from", "")
        if _date_from != "":
            if validate_date(_date_from):
                filters.add(Q(date_added__date__gte=datetime.strptime(_date_from, '%Y-%m-%d')), Q.AND)  # nopep8

        _date_to = request.GET.get("date-to", "")
        if _date_to != "":
            if validate_date(_date_to):
                filters.add(Q(date_added__date__lte=datetime.strptime(_date_to, '%Y-%m-%d')), Q.AND)  # nopep8

        _sold_from = request.GET.get("sold-from", "")
        if _sold_from != "":
            if validate_date(_sold_from):
                filters.add(Q(date_removed__date__gte=datetime.strptime(_sold_from, '%Y-%m-%d')), Q.AND)  # nopep8

        _sold_to = request.GET.get("sold-to", "")
        if _sold_to != "":
            if validate_date(_sold_to):
                filters.add(Q(date_removed__date__lte=datetime.strptime(_sold_to, '%Y-%m-%d')), Q.AND)  # nopep8

        cars = Car.objects.filter(filters)

        return Response({
            'status': status.HTTP_200_OK,
            'total': cars.count()
        }, status=status.HTTP_200_OK)


class makes(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        makes = Make.objects.all().order_by("name").annotate(
            models_count=Count('models', distinct=True),
            cars_count=Count('models__cars', distinct=True)
        )
        serializer = MakeSerializer(instance=makes, many=True)

        return Response({
            'status': status.HTTP_200_OK,
            'makes': serializer.data,
            'queries': len(connection.queries),
        }, status=status.HTTP_200_OK)


class models(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, make_id, format=None):
        make = fetch_make(id=make_id)
        if make is None:
            return create_error_response("Invalid Make")

        models = Model.objects.filter(make=make).order_by("name").annotate(
            cars_count=Count('cars', distinct=True)
        )
        serializer = ModelSerializer(instance=models, many=True)

        return Response({
            'status': status.HTTP_200_OK,
            'models': serializer.data,
            'queries': len(connection.queries),
        }, status=status.HTTP_200_OK)
