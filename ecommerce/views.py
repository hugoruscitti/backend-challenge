from rest_framework import viewsets
from ecommerce import models
from ecommerce import serializers
from rest_framework.exceptions import ValidationError


class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super(OrderViewSet, self).create(request, *args, **kwargs)
        except ValueError as exception:
            raise ValidationError({"validation error": exception})

    def update(self, request, *args, **kwargs):
        try:
            return super(OrderViewSet, self).update(request, *args, **kwargs)
        except ValueError as exception:
            raise ValidationError({"validation error": exception})

