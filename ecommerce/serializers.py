from rest_framework import serializers
from collections import Counter
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

        self.validate_and_create_order_details(order, detail_list)

        return order

    def update(self, instance, validated_data):
        detail_list = validated_data.pop('detail')

        instance.detail.all().delete()

        self.validate_and_create_order_details(instance, detail_list)

        return instance

    def validate_and_create_order_details(self, order, detail_list):
        products = [detail['product'] for detail in detail_list]
        products_with_count = Counter(products)
        products_repeated = [key for key in products_with_count.keys() if products_with_count[key] > 1]

        if products_repeated:
            raise ValueError(f"Repeated product in orders is not allowed")

        for detail in detail_list:
            order.detail.create(product=detail['product'], quantity=detail['quantity'])

