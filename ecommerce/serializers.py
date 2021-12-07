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
    class Meta:
        model = models.Order
        fields = [
            'date_time', 
            'get_total',
        ]
