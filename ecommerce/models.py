from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=30)
    price = models.FloatField(default=0)
    stock = models.IntegerField(default=0)


class Order(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return sum([detail.get_total() for detail in self.orderdetail_set.all()])


class OrderDetail(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    def get_total(self):
        return self.quantity * self.product.price
