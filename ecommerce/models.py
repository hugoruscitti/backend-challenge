from django.db import models
import requests
from django.conf import settings

from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import transaction


class Product(models.Model):
    name = models.CharField(max_length=30)
    price = models.FloatField(default=0)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"<Product {self.name} (id: {self.id})>"


class Order(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return sum([detail.get_total() for detail in self.detail.all()])

    def get_total_usd(self):
        data = requests.get(settings.URL_DOLLAR_WEB_SERVICE).json()

        items_for_dolar_blue = [
                x['casa'] for x in data 
                if 'Dolar Blue' in x['casa']['nombre']
        ]

        value_as_float = float(items_for_dolar_blue[0]['venta'].replace(",", "."))

        return self.get_total() / value_as_float


class OrderDetail(models.Model):
    order = models.ForeignKey('Order', related_name='detail', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    def get_total(self):
        return self.quantity * self.product.price


@receiver(pre_save, sender=OrderDetail, dispatch_uid='change_product_stock')
@transaction.atomic
def change_product_stock(sender, instance, **kwargs):
    if instance.id is None:
        product = instance.product
        product.refresh_from_db()
        product.stock -= instance.quantity

        if product.stock < 0:
            raise ValueError(f"Can't change stock to negative value of product {product}")

        product.save()
    else:
        previous = OrderDetail.objects.get(id=instance.id)

        if previous.quantity != instance.quantity:
            product = instance.product
            product.refresh_from_db()
            product.stock -= instance.quantity - previous.quantity

            if product.stock < 0:
                raise ValueError(f"Can't change stock to negative value of product {product}")

            product.save()

@receiver(pre_delete, sender=OrderDetail, dispatch_uid='restore_stock_when_delete_order_detail')
def restore_stock_when_delete_order_detail(sender, instance, using, **kwargs):
    product = instance.product
    product.refresh_from_db()
    product.stock += instance.quantity
    product.save()
