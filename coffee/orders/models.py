from django.db import models

from django.utils.timezone import now
from django.contrib.auth.admin import User


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category")

    def __str__(self):
        return self.name


class Addon(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0.00)

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=3)

    def __str__(self):
        return self.name


class Location(models.Model):
    address = models.CharField(max_length=200)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="size")
    price = models.FloatField(default=0)

    def __str__(self):
        return str(self.product.name) + " " + str(self.size.name) + " " + str(self.price)


class Client(models.Model):
    user_id = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    register = models.DateTimeField(default=now)
    last_login = models.DateTimeField(auto_now_add=True)
    last_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="location")

    def __str__(self):
        return self.username


class Cart(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client")
    price = models.FloatField(default=0.00)

    def __str__(self):
        return self.client.username


class CartDetail(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    addon = models.ForeignKey(Addon, on_delete=models.CASCADE, related_name="addon")

    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price = models.FloatField(default=0.00)

    # timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return self.cart.client.username


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=200, default="")
    price = models.FloatField(default=0.00)
    paid = models.BooleanField(default=False)
    paid_on = models.DateTimeField(default=now)
    created_on = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.client.username) + " " + str(self.price)


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    addon = models.ForeignKey(Addon, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price = models.FloatField(default=0.00)

    def __str__(self):
        return str(self.order.client.username) + " " + str(self.price)
