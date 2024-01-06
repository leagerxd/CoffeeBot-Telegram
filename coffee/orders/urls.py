from django.urls import path

from .views import *

urlpatterns = [
    path('categories', CategoryAPIView.as_view()),
    path('products', ProductAPIView.as_view()),
    path('addons', AddonAPIView.as_view()),
    path('locations', LocationAPIView.as_view()),

    path('products/<int:product_id>/sizes', ProductSizeAPIView.as_view()),

    path('clients', ClientAPIView.as_view()),
    path('clients/<int:user_id>/orders', OrderAPIView.as_view()),
    path('clients/<int:user_id>/cart', Cart.as_view()),
    path('clients/<int:user_id>/location', UserLocation.as_view())
]
