from datetime import datetime
import math

from django.db import connection
from django.db.models import Q, Count
from django.db.models.functions import ExtractWeekDay

from rest_framework import status, authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from birkoss.helpers import create_error_response, validate_date, create_error_message  # nopep8
from dealers.models import fetch_dealer
from cars.models import Car, CarHistory, Make, Model, fetch_car, fetch_make, fetch_model  # nopep8

from .serializers import CarSerializer, CarQuerySerializer, CarWriteSerializer, CarPatchSerializer, HistorySerializer, MakeSerializer, ModelSerializer, SaleSerializer  # nopep8


class cars(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        filters = Q()

        cars = Car.objects.filter(
            filters
        ).order_by(
            "-date_added"
        ).select_related("model").select_related("model__make")

        total_cars = len(cars)

        limit = 5
        _limit = request.GET.get("limit", 5)
        if _limit is not None or _limit.isnumeric():
            # @TODO: Warn when over or under the limit
            limit = min(100, max(5, int(_limit)))

        page = 1
        _page = request.GET.get("page", 1)
        if _page is not None or _page.isnumeric():
            # @TODO: Warn when over or under the page limitx
            page = max(1, int(_page))

        serializer = CarQuerySerializer(
            instance=cars[(page - 1) * limit: page * limit],
            many=True
        )

        return Response({
            'status': status.HTTP_200_OK,
            'cars': serializer.data,
            'queries': len(connection.queries),
            'cars_count': total_cars,
            'pages_count': math.ceil(total_cars / limit)
        }, status=status.HTTP_200_OK)


class dealer_cars(APIView):
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
        car.sold_days_count = (
            car.date_removed.date() - car.date_added.date()
        ).days
        car.save()

        return Response({
            'status': status.HTTP_200_OK
        }, status=status.HTTP_200_OK)

    def patch(self, request, car_id, format=None):
        car = fetch_car(id=car_id)
        if car is None:
            return create_error_response("Invalid Car")

        serializer = CarPatchSerializer(data=request.data)

        if serializer.is_valid():
            changed_fields = []

            # Verify the car has change
            for field in serializer.data:
                if str(getattr(car, field)) != str(serializer.data[field]):
                    changed_fields.append(field)
            if len(changed_fields) == 0:
                return Response({
                    'status': status.HTTP_304_NOT_MODIFIED,
                })

            # Save the history
            for field in changed_fields:
                history = CarHistory(
                    car=car,
                    field=field,
                    value=getattr(car, field)
                )
                history.save()

            # Update the car
            serializer.update(car, serializer.data)
            return Response({
                'status': status.HTTP_200_OK,
            })

        return create_error_response(
            create_error_message(serializer.errors)
        )


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


class stats_weekly_cars(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):

        filters = Q()

        _condition = request.GET.get("condition", "")
        if _condition == "used" or _condition == "new":
            filters.add(Q(condition=_condition), Q.AND)

        weekday = {}

        _date_from = request.GET.get("date-from", "")
        _date_to = request.GET.get("date-to", "")

        _status = request.GET.get("status", "sold")
        if _status == "sold":
            filters.add(~Q(date_removed=None), Q.AND)
            weekday['weekday'] = ExtractWeekDay('date_removed')

            if _date_to != "":
                if validate_date(_date_to):
                    filters.add(
                        Q(
                            date_removed__date__lte=datetime.strptime(
                                _date_to,
                                '%Y-%m-%d'
                            )
                        ),
                        Q.AND
                    )
            if _date_from != "":
                if validate_date(_date_from):
                    filters.add(
                        Q(
                            date_removed__date__gte=datetime.strptime(
                                _date_from,
                                '%Y-%m-%d'
                            )
                        ),
                        Q.AND
                    )

        else:
            filters.add(Q(date_removed=None), Q.AND)
            weekday['weekday'] = ExtractWeekDay('date_added')

            if _date_to != "":
                if validate_date(_date_to):
                    filters.add(
                        Q(
                            date_added__date__lte=datetime.strptime(
                                _date_to,
                                '%Y-%m-%d'
                            )
                        ),
                        Q.AND
                    )
            if _date_from != "":
                if validate_date(_date_from):
                    filters.add(
                        Q(
                            date_added__date__gte=datetime.strptime(
                                _date_from,
                                '%Y-%m-%d'
                            )
                        ),
                        Q.AND
                    )

        cars = Car.objects.filter(
            filters
        ).annotate(
            **weekday
        ).values(
            "weekday"
        ).annotate(
            cars_count=Count("id")
        ).values(
            "weekday",
            "cars_count"
        ).order_by(
            "weekday"
        )

        return Response({
            'status': status.HTTP_200_OK,
            'total': cars,
        }, status=status.HTTP_200_OK)


class makes(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        filters = Q()

        dealers = request.GET.getlist("dealers[]", [])
        if len(dealers) > 0:
            subfilters = Q()
            for dealer in dealers:
                subfilters.add(Q(models__cars__dealer_id=dealer), Q.OR)
            filters.add(subfilters, Q.AND)

        makes = Make.objects.filter(filters).order_by("name").annotate(
            models_count=Count('models', distinct=True),
            cars_count=Count('models__cars', distinct=True)
        )
        serializer = MakeSerializer(instance=makes, many=True)

        return Response({
            'status': status.HTTP_200_OK,
            'makes': serializer.data,
            'queries': len(connection.queries),
        }, status=status.HTTP_200_OK)


class makes_models(APIView):
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


class models(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        filters = Q()

        dealers = request.GET.getlist("dealers[]", [])
        if len(dealers) > 0:
            subfilters = Q()
            for dealer in dealers:
                subfilters.add(Q(cars__dealer_id=dealer), Q.OR)
            filters.add(subfilters, Q.AND)

        makes = request.GET.getlist("makes[]", [])
        if len(makes) > 0:
            subfilters = Q()
            for make in makes:
                subfilters.add(Q(make_id=make), Q.OR)
            filters.add(subfilters, Q.AND)

        models = Model.objects.filter(filters).order_by("name").annotate(
            cars_count=Count('cars', distinct=True)
        )
        serializer = ModelSerializer(instance=models, many=True)

        return Response({
            'status': status.HTTP_200_OK,
            'models': serializer.data,
            'queries': len(connection.queries),
        }, status=status.HTTP_200_OK)


class histories(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        histories = CarHistory.objects.all().select_related("car").annotate(
            histories_count=Count("car__histories")
        ).select_related("car__model").select_related("car__model__make").order_by("-date_added")  # nopep8
        serializer = HistorySerializer(instance=histories, many=True)

        return Response({
            'status': status.HTTP_200_OK,
            'histories': serializer.data,
            'queries': len(connection.queries),
        }, status=status.HTTP_200_OK)


class sales(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        cars = Car.objects.filter(
            ~Q(date_removed=None)
        ).values(
            "sold_days_count"
        ).annotate(
            cars_count=Count("sold_days_count")
        ).order_by(
            "sold_days_count"
        )

        serializer = SaleSerializer(instance=cars, many=True)

        return Response({
            'status': status.HTTP_200_OK,
            'sales': serializer.data,
            'queries': len(connection.queries),
        }, status=status.HTTP_200_OK)
