from django.shortcuts import render
from rest_framework import serializers, viewsets
from ecommerce import models

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Product
        fields = [
            'name', 
            'price',
            'stock',
        ]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = ProductSerializer
