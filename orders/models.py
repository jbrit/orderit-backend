from django.db import models

from utilities.constants import CATEGORIES, STATUSES
from vauth.models import User
from wallet.models import Transaction
# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    category = models.CharField(max_length=2, choices=CATEGORIES)
    stock = models.IntegerField()
    
    def __str__(self):
        return self.name

class Meal(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=2, choices=CATEGORIES)
    items = models.ManyToManyField(Item)

    @property
    def total_price(self):
        return self.items.all().aggregate(models.Sum('price'))


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(max_length=2, choices=STATUSES)
    
    @property
    def paid(self):
        return self.transaction == True

    
    @property
    def total_order_price(self):
        return self.orderitem_set.all().aggregate(models.Sum('ordered_price'))


class OrderItem(models.Model):
    meal = models.OneToOneField(Meal, on_delete=models.PROTECT, null=True, blank=True)
    item = models.OneToOneField(Item, on_delete=models.PROTECT, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True)
    ordered_price = models.FloatField()
    quantity = models.IntegerField()
