from django.contrib import admin

from .models import (
    Category,
    Product,
    Size,
    Location,
    Price,
    Addon,
    Client,
    Cart,
    CartDetail,
    Order,
    OrderDetail
)

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Size)
admin.site.register(Location)
admin.site.register(Price)
admin.site.register(Addon)
admin.site.register(Client)
admin.site.register(Cart)
admin.site.register(CartDetail)
admin.site.register(Order)
admin.site.register(OrderDetail)
