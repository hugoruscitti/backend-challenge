from django.test import TestCase
from django.contrib.auth.models import User
from ecommerce import models
from rest_framework.test import APITestCase
from mock import patch
import requests


class BasicTestCase(TestCase):

    def test_get_total_in_orders(self):
        watch = models.Product.objects.create(name="watch", price=99.00)
        chair = models.Product.objects.create(name="chair", price=1000.00)

        order = models.Order.objects.create()
        order.orderdetail_set.create(product=watch, quantity=5)
        order.orderdetail_set.create(product=chair, quantity=1)

        self.assertEqual(order.get_total(), 1495.00)


class ProductAPITestCase(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user('admin', 'admin')
        self.client.force_authenticate(user=self.admin_user)

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

    def test_list_products(self):
        watch = models.Product.objects.create(name="watch", price=99.00)
        monitor = models.Product.objects.create(name="monitor", price=800.00)

        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_get_product(self):
        watch = models.Product.objects.create(name="watch", price=99.00)

        response = self.client.get(f"/api/products/{watch.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "name": "watch",
            "price": 99.0,
            "stock": 0,
        })

    def test_can_remove_product_with_user(self):
        watch = models.Product.objects.create(name="watch", price=99.00)

        response = self.client.delete(f"/api/products/{watch.id}/")
        self.assertEqual(response.status_code, 204)


class OrderAPITestCase(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user('admin', 'admin')
        self.client.force_authenticate(user=self.admin_user)

    def test_list_no_orders(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_list_with_one_order(self):
        watch = models.Product.objects.create(name="watch", price=99.00)

        response = self.client.get("/api/orders/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])


    @patch.object(requests, 'get')
    def test_get_order_with_total_usd(self, mock_requests):
        watch = models.Product.objects.create(name="watch", price=100.00)

        order = models.Order.objects.create()
        order.orderdetail_set.create(product=watch, quantity=1)

        mock_requests.return_value.json.return_value = [
                {
                    'casa': {
                        'compra': '195,00', 
                        'venta': '200,00',
                        'agencia': '310',
                        'nombre': 'Dolar Blue',
                        'variacion': '-0,50',
                        'ventaCero': 'TRUE',
                        'decimales': '2',
                    }
                }
        ]


        response = self.client.get(f"/api/orders/{order.id}/")

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertEqual(response_data['total_usd'], 0.5)
