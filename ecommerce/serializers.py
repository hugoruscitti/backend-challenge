from rest_framework import serializers
from ecommerce import models

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Product
        fields = [
            'name', 
            'price',
            'stock',
        ]

class OrderSerializer(serializers.HyperlinkedModelSerializer):
    total_usd = serializers.SerializerMethodField()

    class Meta:
        model = models.Order
        fields = [
            'date_time', 
            'get_total',
            'total_usd',
        ]


    def get_total_usd(self, obj):
        return obj.get_total_usd()
