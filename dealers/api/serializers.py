from rest_framework import serializers

from ..models import Dealer


class DealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealer
        fields = ['id', 'name', 'address', 'city', 'postal_code', 'website', 'latitude', 'longitude', 'api_key', 'feeds_url']
