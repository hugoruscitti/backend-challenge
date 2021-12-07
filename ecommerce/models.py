from django.db import models
import requests
from django.conf import settings

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=30)
    price = models.FloatField(default=0)
    stock = models.IntegerField(default=0)


class Order(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return sum([detail.get_total() for detail in self.orderdetail_set.all()])

    def get_total_usd(self):
        data = requests.get(settings.URL_DOLLAR_WEB_SERVICE).json()

        items_for_dolar_blue = [
                x['casa'] for x in data 
                if 'Dolar Blue' in x['casa']['nombre']
        ]

        value_as_float = float(items_for_dolar_blue[0]['venta'].replace(",", "."))

        return self.get_total() / value_as_float


class OrderDetail(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    def get_total(self):
        return self.quantity * self.product.price
