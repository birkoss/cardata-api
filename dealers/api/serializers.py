from rest_framework import serializers

from ..models import Dealer


class DealerSerializer(serializers.ModelSerializer):
    cars_count = serializers.CharField()
    active_cars_count = serializers.CharField()
    sold_cars_count = serializers.CharField()

    class Meta:
        model = Dealer
        fields = [
            'id',
            'name',
            'address',
            'city',
            'postal_code',
            'website',
            'latitude',
            'longitude',
            'api_key',
            'feeds_url',
            'cars_count',
            'active_cars_count',
            'sold_cars_count',
        ]
