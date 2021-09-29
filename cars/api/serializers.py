from rest_framework import serializers

from ..models import Car, Model, Make


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
