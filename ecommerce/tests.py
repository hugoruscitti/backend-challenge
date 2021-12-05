from django.test import TestCase
from ecommerce import models

class BasicTestCase(TestCase):

    def test_get_total_in_orders(self):
        watch = models.Product.objects.create(name="watch", price=99.00)
        chair = models.Product.objects.create(name="chair", price=1000.00)

        order = models.Order.objects.create()
        order.orderdetail_set.create(product=watch, quantity=5)
        order.orderdetail_set.create(product=chair, quantity=1)

        self.assertEqual(1495.00, order.get_total())
