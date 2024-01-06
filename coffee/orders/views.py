from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from rest_framework.views import APIView
from .services import (
    get_categories,
    get_products,
    get_addons,
    get_locations,
    get_location,
    set_location,
    get_product_sizes,
    get_client,
    get_cart_content,
    get_order_history,
    add_cart_to_order,
    add_order_to_cart,
    add_client,
    get_or_create_client,
    add_product_to_cart,
    remove_product_from_cart
)


class CategoryAPIView(APIView):
    def get(self, request):
        categories = get_categories()
        return JsonResponse(categories, safe=False)


# Create your views here.
class ProductAPIView(APIView):
    def get(self, request):
        product_id = request.GET.get('product_id')
        category_id = request.GET.get('category_id')
        if category_id:
            products = get_products(category_id=category_id)
        else:
            products = get_products(product_id=product_id)

        return JsonResponse(products, safe=False)


class AddonAPIView(APIView):
    def get(self, request):
        addons = get_addons()
        return JsonResponse(addons, safe=False)


class ProductSizeAPIView(APIView):
    def get(self, request, product_id):
        sizes = get_product_sizes(product_id)
        return JsonResponse(sizes, safe=False)


class LocationAPIView(APIView):
    def get(self, request):
        locations = get_locations()
        return JsonResponse(locations, safe=False)


class UserLocation(APIView):
    def get(self, request, user_id):
        location = get_location(user_id)
        return JsonResponse(location, safe=False)

    def post(self, request, user_id):
        location_id = request.POST.get('location_id')
        status = set_location(user_id, location_id)
        return JsonResponse({"status": status}, safe=False)


class ClientAPIView(APIView):
    def get(self, request, user_id=""):
        context = get_client()
        return JsonResponse(context, safe=False)

    def post(self, request):
        get_or_create_client(dict(request.POST))
        return HttpResponse("Ok")


class Cart(APIView):
    def get(self, request, user_id):
        cart = get_cart_content(user_id)
        return JsonResponse(cart, safe=False)

    def post(self, request, user_id):
        order_id = request.POST.get('order_id')
        if order_id:
            return JsonResponse(add_order_to_cart(user_id, order_id), safe=False)
        else:
            status = add_product_to_cart(user_id, request.POST.get('product_id'), request.POST.get('size_id'),
                                         request.POST.get('addon_id'))
        return JsonResponse({"status": status}, safe=False)

    def delete(self, request, user_id):
        product_id = request.GET.get('product_id')
        status = remove_product_from_cart(user_id, product_id)
        return JsonResponse({"status": status}, safe=False)


class OrderAPIView(APIView):
    def get(self, request, user_id):
        orders = get_order_history(user_id)
        return JsonResponse(orders, safe=False)

    def post(self, request, user_id):
        status = add_cart_to_order(user_id)
        context = {"status": status}
        return JsonResponse(context, safe=False)
