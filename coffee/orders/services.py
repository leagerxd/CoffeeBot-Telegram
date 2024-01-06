from .models import *
from .serializers import *

from datetime import datetime


def get_categories():
    categories = Category.objects.all()
    return CategorySerializer(categories, many=True).data


def get_products(category_id=None, product_id=None):
    if product_id:
        if Product.objects.filter(product=product_id).exists():
            products = Product.objects.get(id=product_id)
    elif category_id:
        if Product.objects.filter(category=category_id).exists():
            products = Product.objects.filter(category=category_id)
    else:
        products = Product.objects.all()

    return ProductSerializer(products, many=True).data


def get_addons():
    addons = Addon.objects.all()
    return AddonSerializer(addons, many=True).data


def get_locations():
    locations = Location.objects.all()
    return LocationSerializer(locations, many=True).data


def get_location(user_id):
    client = Client.objects.get(user_id=user_id)
    return LocationSerializer(client.last_location).data


def set_location(user_id, location_id):
    client = Client.objects.get(user_id=user_id)
    serializer = ClientSerializer(client, data={"location": location_id}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return "ok"
    else:
        return "error"


def get_product_sizes(product_id):
    result = {}
    if Price.objects.filter(product=product_id).exists():
        product = Price.objects.filter(product=product_id)
        for item in product:
            result.update({
                item.size.id: {
                    "name": item.size.name,
                    "price": item.price
                }
            })

    return result


def add_client(data):
    data.update({"location": Location.objects.first()})
    if Client.objects.filter(user_id=data['user_id']).exists():
        client = Client.objects.get(user_id=data['user_id'])
        serializer = ClientSerializer(client, data=data)
    else:
        serializer = ClientSerializer(data=data)

    if serializer.is_valid():
        serializer.save()


def get_or_create_client(data):
    for value in data:
        data[value] = data[value][0]

    data.update({"last_location": Location.objects.first().id})
    if Client.objects.filter(user_id=data.get("user_id")).exists():
        client = Client.objects.filter(user_id=data.get("user_id"))
        serializer = ClientSerializer(client, data=data, partial=True)
    else:
        serializer = ClientSerializer(data=data)
    if serializer.is_valid():
        serializer.save()


def get_client(user_id=""):
    if user_id:
        if Client.objects.filter(user_id=user_id).exists():
            data = Client.objects.filter(user_id=user_id)
    else:
        data = Client.objects.all()

    return ClientSerializer(data, many=True).data


def get_or_create_cart(user_id):
    if Cart.objects.filter(client__user_id=user_id).exists():
        cart = Cart.objects.get(client__user_id=user_id)
    else:
        data = {
            "client": Client.objects.get(user_id=user_id).id,
            "price": 0.00
        }

        serializer = CartSerializer(data=data)

        if serializer.is_valid():
            cart = serializer.save()
        else:
            return

    return cart


def get_cart_details(user_id):
    cart = get_or_create_cart(user_id)
    return CartDetail.objects.filter(cart_id=cart.id)


def get_cart_content(user_id):
    cart = get_or_create_cart(user_id)
    cart_details = CartDetail.objects.filter(cart=cart.id)
    result = []
    for item in cart_details:
        result.append({
            "id": item.id,
            "product_id": item.product.id,
            "name": item.product.name,
            "size": item.size.name,
            "addon": item.addon.name,
            "price": item.price
        })

    return result


def update_cart(cart_id, price):
    if Cart.objects.filter(id=cart_id).exists():
        cart = Cart.objects.get(id=cart_id)
        serializer = CartSerializer(cart, data={"price": round(cart.price + price, 2)}, partial=True)
        if serializer.is_valid():
            serializer.save()


def get_product_price(product_id, size_id, addon_id):
    if Price.objects.filter(product=product_id, size=size_id).exists():
        basic_price = Price.objects.get(product=product_id, size=size_id).price
    else:
        basic_price = 0

    if Addon.objects.filter(id=addon_id).exists():
        addon_price = Addon.objects.get(id=addon_id).price
    else:
        addon_price = 0

    return round(basic_price + addon_price, 2)


def add_product_to_cart(user_id, product_id, size_id, addon_id):
    price = get_product_price(product_id, size_id, addon_id)

    cart = get_or_create_cart(user_id)
    update_cart(cart.id, price)

    data = {
        "cart": cart.id,
        "product": product_id,
        "addon": addon_id,
        "size": size_id,
        "price": price,
        "timestamp": datetime.now()
    }

    serializer = CartDetailSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return "ok"
    else:
        return "error"


def remove_product_from_cart(user_id, product_id):
    cart = get_or_create_cart(user_id)
    if CartDetail.objects.filter(id=product_id, cart=cart.id).exists():
        product = CartDetail.objects.get(id=product_id, cart=cart.id)
        update_cart(cart.id, - (product.price))
        product.delete()
        return "ok"
    else:
        return "not found"


def get_or_create_order(user_id):
    orders = get_order_history(user_id)
    client = Client.objects.get(user_id=user_id)
    data = {
        "client": client.id,
        "location": client.last_location.id,
        "transaction_id": "0",
        "price": 0.00,
        "paid": False,
        "created_on": now()
    }

    if len(orders) == 0:
        serializer = OrderSerializer(data=data)
    elif not orders[0]['paid']:
        serializer = OrderSerializer(data=data)
    else:
        return orders[0]

    print(data)
    if serializer.is_valid():
        print("saved")
        order = serializer.save()
    else:
        return

    return order


def get_order_content(order_id):
    return OrderDetailSerializer(OrderDetail.objects.filter(order=order_id), many=True).data


def add_cart_to_order(user_id):
    cart_content = get_cart_details(user_id)

    order = get_or_create_order(user_id)

    price = 0
    for product in cart_content:
        data = CartDetailSerializer(product).data
        price += data['price']
        data.update({"order": order.id})
        serializer = OrderDetailSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            product.delete()

    serializer = OrderSerializer(order, data={"price": price}, partial=True)

    if serializer.is_valid():
        serializer.save()


def add_order_to_cart(user_id, order_id):
    cart = get_or_create_cart(user_id)
    order_content = get_order_content(order_id)
    for item in order_content:
        item.pop('order')
        item.pop('id')
        # item.update({"name": Product.objects.get(id=item['product']).name})
        item.update({"size": Size.objects.get(id=item['size']).id})
        item.update({"addon": Addon.objects.get(id=item['addon']).id})
        # item.update({"product_id": item['product']})
        item.update({"cart": cart.id})

        print(item)
        serializer = CartDetailSerializer(data=item)

        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save()

    cart_content = get_cart_content(user_id)
    return cart_content


def get_order_history(user_id):
    orders = Order.objects.filter(client__user_id=user_id).order_by("-created_on")
    return OrderSerializer(orders, many=True).data


def get_order(order_id=0):
    if Order.objects.filter(id=order_id).exists():
        order = Order.objects.get(id=order_id)
    else:
        order = Order.objects.all()

    serializer = OrderSerializer(order, many=True)

    return serializer.data
