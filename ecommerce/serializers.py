from rest_framework import serializers
from ecommerce import models

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = [
            'id',
            'name', 
            'price',
            'stock',
        ]

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderDetail
        fields = [
            'id',
            'product',
            'quantity',
        ]

class OrderSerializer(serializers.ModelSerializer):
    total_usd = serializers.SerializerMethodField()
    detail = OrderDetailSerializer(many=True)

    class Meta:
        model = models.Order
        fields = [
            'date_time', 
            'get_total',
            'total_usd',
            'detail',
        ]

    def get_total_usd(self, obj):
        return obj.get_total_usd()

    def create(self, validated_data):
        detail_list = validated_data.pop('detail')
        order = models.Order.objects.create(**validated_data)

        for detail in detail_list:
            order.detail.create(product=detail['product'], quantity=detail['quantity'])

        return order

    def update(self, instance, validated_data):
        detail_list = validated_data.pop('detail')

        instance.detail.all().delete()

        for detail in detail_list:
            instance.detail.create(product=detail['product'], quantity=detail['quantity'])

        return instance
