from django.test import TestCase
from django.contrib.auth.models import User
from ecommerce import models
from rest_framework.test import APITestCase
from mock import patch
import requests


class BasicTestCase(TestCase):

    def test_get_total_in_orders(self):
        watch = models.Product.objects.create(name="watch", price=99.00, stock=10)
        chair = models.Product.objects.create(name="chair", price=1000.00, stock=10)

        order = models.Order.objects.create()
        order.detail.create(product=watch, quantity=5)
        order.detail.create(product=chair, quantity=1)

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
            "id": 1,
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
            "id": 1,
            "name": "watch",
            "price": 99.0,
            "stock": 0,
        })

    def test_can_remove_product_with_user(self):
        watch = models.Product.objects.create(name="watch", price=99.00)

        response = self.client.delete(f"/api/products/{watch.id}/")
        self.assertEqual(response.status_code, 204)

    def test_create_a_product(self):
        response = self.client.post(f"/api/products/", {"name": "watch", "price": 99.00})
        self.assertEqual(response.status_code, 201)

        self.assertEqual(models.Product.objects.count(), 1)

    def test_change_product_stock(self):
        response = self.client.post(f"/api/products/", {"name": "watch", "price": 99.00, "stock": 10})
        self.assertEqual(response.status_code, 201)

        response = self.client.patch("/api/products/1/", {"stock": 20}, format="json")

        self.assertEqual(response.status_code, 200)

        product = models.Product.objects.get(id=1)
        self.assertEqual(product.stock, 20)

    def test_can_editor_a_product(self):
        response = self.client.post(f"/api/products/", {"name": "watch", "price": 99.00})
        self.assertEqual(response.status_code, 201)

        product_id = response.json()['id']
        response = self.client.patch(f"/api/products/{product_id}/", {"name": "watch new model", "price": 200.00})
        self.assertEqual(response.status_code, 200)

        product = models.Product.objects.get(pk=1)
        self.assertEqual(product.name, "watch new model")
        self.assertEqual(product.price, 200.0)



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
        watch = models.Product.objects.create(name="watch", price=100.00, stock=1)

        order = models.Order.objects.create()
        order.detail.create(product=watch, quantity=1)

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

    def test_get_order_with_detail(self):
        watch = models.Product.objects.create(name="watch", price=99.00, stock=10)
        order = models.Order.objects.create()

        order.detail.create(product=watch, quantity=2)
        order.save()

        watch.refresh_from_db()

        response = self.client.get(f"/api/orders/{order.id}/")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()['detail'], [{
                "id": 1, 
                "product": watch.id, 
                "quantity": 2,
            }
        ])

    def test_create_order_with_detail(self):
        watch = models.Product.objects.create(name="watch", price=99.00, stock=10)

        response = self.client.post("/api/orders/", {
            "detail": [
                {
                    "product": watch.id, 
                    "quantity": 1,
                },
                {
                    "product": watch.id, 
                    "quantity": 2,
                },
            ]
        }, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.json()['detail']), 2)

        watch.refresh_from_db()
        self.assertEqual(watch.stock, 7)

    def test_restore_stock_when_delete_order(self):
        watch = models.Product.objects.create(name="watch", price=99.00, stock=10)

        response = self.client.post("/api/orders/", {
            "detail": [
                {
                    "product": watch.id, 
                    "quantity": 5,
                },
            ]
        }, format="json")

        watch.refresh_from_db()
        self.assertEqual(watch.stock, 5)

        response = self.client.delete("/api/orders/1/")
        self.assertEqual(response.status_code, 204)

        watch.refresh_from_db()
        self.assertEqual(watch.stock, 10)

    def test_cant_change_order_with_invalid_stock(self):
        watch = models.Product.objects.create(name="watch", price=99.00, stock=10)

        response = self.client.post("/api/orders/", {
            "detail": [
                {
                    "product": watch.id, 
                    "quantity": 5,
                },
            ]
        }, format="json")

        self.assertEqual(response.status_code, 201)

        watch.refresh_from_db()
        self.assertEqual(watch.stock, 5)

        response = self.client.patch("/api/orders/1/", {
            "detail": [
                {
                    "product": watch.id, 
                    "quantity": 16,
                },
            ]
        }, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(watch.stock, 5)

    def test_can_change_order(self):
        watch = models.Product.objects.create(name="watch", price=99.00, stock=10)

        response = self.client.post("/api/orders/", {
            "detail": [
                {
                    "product": watch.id, 
                    "quantity": 5,
                },
            ]
        }, format="json")

        watch.refresh_from_db()
        self.assertEqual(watch.stock, 5)

        response = self.client.patch("/api/orders/1/", {
            "detail": [
                {
                    "product": watch.id, 
                    "quantity": 10,
                },
            ]
        }, format="json")

        watch.refresh_from_db()
        self.assertEqual(watch.stock, 0)

    def test_change_stock_when_order_detail_change(self):
        watch = models.Product.objects.create(name="watch", price=99.00, stock=10)

        order = models.Order.objects.create()
        order_detail = order.detail.create(product=watch, quantity=5)

        watch.refresh_from_db()
        self.assertEqual(watch.stock, 5)

        order_detail.quantity = 7
        order_detail.save()

        watch.refresh_from_db()
        self.assertEqual(watch.stock, 3)

    def test_cant_create_order_with_quantity_0_or_minor(self):
        watch = models.Product.objects.create(name="watch", price=99.00, stock=10)

        response = self.client.post("/api/orders/", {
            "detail": [
                {
                    "product": watch.id, 
                    "quantity": 0,
                },
            ]
        }, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(watch.stock, 10)
        self.assertEqual(response.json()['validation error'], "Quantity can't be less than 1")
