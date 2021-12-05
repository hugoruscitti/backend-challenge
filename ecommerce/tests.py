from django.test import TestCase
from ecommerce import models
from rest_framework.test import APITestCase

class BasicTestCase(TestCase):

    def test_get_total_in_orders(self):
        watch = models.Product.objects.create(name="watch", price=99.00)
        chair = models.Product.objects.create(name="chair", price=1000.00)

        order = models.Order.objects.create()
        order.orderdetail_set.create(product=watch, quantity=5)
        order.orderdetail_set.create(product=chair, quantity=1)

        self.assertEqual(order.get_total(), 1495.00)


class ProductAPITestCase(APITestCase):

    def test_list_no_products(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_list_with_one_product(self):
        watch = models.Product.objects.create(name="watch", price=99.00)

        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{
            "name": "watch",
            "price": 99.0,
            "stock": 0,
        }])
