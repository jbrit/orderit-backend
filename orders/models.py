from django.db import models

from utilities.constants import CATEGORIES, STATUSES
from utilities.images import image_resize
from vauth.models import User
from wallet.models import Transaction

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="items", null=True)
    price = models.FloatField()
    category = models.CharField(max_length=2, choices=CATEGORIES)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        image_resize(self.image, 1000,1000)
        super().save(*args, **kwargs)


class Meal(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="meals", null=True)
    category = models.CharField(max_length=2, choices=CATEGORIES)
    items = models.ManyToManyField(Item)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        image_resize(self.image, 1000,1000)
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.items.all().aggregate(models.Sum("price"))


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    transaction = models.ForeignKey(
        Transaction, on_delete=models.PROTECT, null=True, blank=True
    )
    status = models.CharField(max_length=2, choices=STATUSES, default="P")
    vendor = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, related_name="vendor"
    )
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        if self.transaction:
            return f"{self.user.email} - {self.transaction.reference}"
        return self.user.email

    @property
    def reference(self):
        return self.transaction.reference if self.transaction else None

    @property
    def paid(self):
        return self.transaction == True

    @property
    def total_order_price(self):
        return self.orderitem_set.all().aggregate(
            sum=models.Sum(models.F("ordered_price") * models.F("quantity"))
        )["sum"]


class OrderItem(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.PROTECT, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True)
    ordered_price = models.FloatField()
    quantity = models.IntegerField(default=1)


    def __str__(self):
        if self.meal:
            return f"{self.meal.name} - {self.order.user.email}"
        elif self.item:
            return f"{self.item.name} - {self.order.user.email}"
        else:
            return self.order.user.email
