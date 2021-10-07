from rest_framework import serializers

from ..models import Car, CarHistory, Model, Make


class MakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Make
        fields = ['name']


class ModelSerializer(serializers.ModelSerializer):
    # make = MakeSerializer(read_only=True)
    make = serializers.CharField(source="make.name", read_only=True)

    class Meta:
        model = Model
        fields = ['name', 'make']


class CarQuerySerializer(serializers.ModelSerializer):
    model = serializers.CharField(source="model.name", read_only=True)
    make = serializers.CharField(source="model.make.name", read_only=True)

    exterior_color = serializers.CharField(source='raw_exterior_color')
    interior_color = serializers.CharField(source='raw_interior_color')
    body_style = serializers.CharField(source='raw_body_style')
    transmission = serializers.CharField(source='raw_transmission')
    fuel_type = serializers.CharField(source='raw_fuel_type')
    drivetrain = serializers.CharField(source='raw_drivetrain')

    class Meta:
        model = Car
        fields = [
            'id',
            'date_added',
            'make',
            'model',
            'trim',
            'year',
            'price',
            'special_price',
            'vin',
            'mileage',
            'images_count',
            'condition',
            'exterior_color',
            'interior_color',
            'body_style',
            'transmission',
            'fuel_type',
            'drivetrain',
        ]


class CarSerializer(serializers.ModelSerializer):
    model = serializers.CharField(source="model.name", read_only=True)
    make = serializers.CharField(source="model.make.name", read_only=True)

    exterior_color = serializers.CharField(source='raw_exterior_color')
    interior_color = serializers.CharField(source='raw_interior_color')
    body_style = serializers.CharField(source='raw_body_style')
    transmission = serializers.CharField(source='raw_transmission')
    fuel_type = serializers.CharField(source='raw_fuel_type')
    drivetrain = serializers.CharField(source='raw_drivetrain')

    class Meta:
        model = Car
        fields = [
            'id',
            'make',
            'model',
            'trim',
            'year',
            'price',
            'special_price',
            'vin',
            'mileage',
            'images_count',
            'condition',
            'exterior_color',
            'interior_color',
            'body_style',
            'transmission',
            'fuel_type',
            'drivetrain',
        ]


class CarWriteSerializer(serializers.ModelSerializer):
    model = serializers.CharField(source="model.name", read_only=True)
    make = serializers.CharField(source="model.make.name", read_only=True)

    exterior_color = serializers.CharField(source='raw_exterior_color', allow_blank=True)  # nopep8
    interior_color = serializers.CharField(source='raw_interior_color', allow_blank=True)  # nopep8
    body_style = serializers.CharField(source='raw_body_style', allow_blank=True)  # nopep8
    transmission = serializers.CharField(source='raw_transmission', allow_blank=True)  # nopep8
    fuel_type = serializers.CharField(source='raw_fuel_type', allow_blank=True)  # nopep8
    drivetrain = serializers.CharField(source='raw_drivetrain', allow_blank=True)  # nopep8

    class Meta:
        model = Car
        fields = [
            'make',
            'model',
            'trim',
            'year',
            'price',
            'special_price',
            'vin',
            'mileage',
            'images_count',
            'condition',
            'exterior_color',
            'interior_color',
            'body_style',
            'transmission',
            'fuel_type',
            'drivetrain',
        ]


class CarPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            'year',
            'price',
            'special_price',
            'vin',
            'mileage',
            'images_count',
        ]


class MakeSerializer(serializers.ModelSerializer):
    models_count = serializers.CharField()
    cars_count = serializers.CharField()

    class Meta:
        model = Make
        fields = [
            'id',
            'name',
            'models_count',
            'cars_count'
        ]


class MakeSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Make
        fields = [
            'id',
            'name',
        ]


class ModelSerializer(serializers.ModelSerializer):
    make = MakeSimpleSerializer(read_only=True)
    cars_count = serializers.CharField()

    class Meta:
        model = Model
        fields = [
            'id',
            'name',
            'make',
            'cars_count'
        ]


class HistorySerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)
    histories_count = serializers.CharField()

    class Meta:
        model = CarHistory
        fields = [
            'id',
            'date_added',
            'car',
            'field',
            'value',
            'histories_count'
        ]


class SaleSerializer(serializers.ModelSerializer):
    cars_count = serializers.CharField()

    class Meta:
        model = Car
        fields = [
            'cars_count',
            'sold_days_count'
        ]
