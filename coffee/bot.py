import os
import asyncio
import httpx
import ssl
import urllib3
from io import StringIO
from PIL import Image

from datetime import datetime
from pytz import timezone

from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton

from dotenv import load_dotenv

load_dotenv('.env')

bot_token = os.getenv('BOT_TOKEN')

bot = AsyncTeleBot(bot_token)
# API_URL = "http://localhost:8000/"
API_URL = "https://coffee.tdevsdsp.org/"

start_message = """\
Привіт! Я бот кав'ярні. Давай я допоможу тобі зробити твоє перше замовлення!
Тисни кнопку меню для початку!
"""

'''
@bot.message_handler(commands=['clients'])
async def list_users(message):
    data = {
        "chat_id": message.chat.id,
        "user_id": message.from_user.id,
        "first_name": message.from_user.first_name,
        "username": message.from_user.username
    }
    with httpx.Client() as client:
        resp = client.post(API_URL + "/client")

@bot.message_handler(commands=['coffees'])
async def list_coffee(message):
    with httpx.Client() as client:
        resp = client.get(API_URL + "/coffee")
        data = resp.json()
        with httpx.Client() as client:
            resp = urllib3.request("GET", API_URL + data[0]['img'])
            #photo = StringIO(resp.data)

            #photo = Image(resp.text)
            await bot.send_photo(message.chat.id, resp.data)

        #await bot.send_message(message.chat.id, data)


@bot.message_handler(commands=['orders'])
async def list_orders(message):
    with httpx.Client() as client:
        resp = client.get(API_URL + "/order")
        print(resp.json())

# Command /start
@bot.message_handler(commands=['menu'])
async def start(message):

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = InlineKeyboardButton("Menu")
    item2 = InlineKeyboardButton("menu", callback_data="menu")

    markup.add(item1)
    markup.add(item2)

    await bot.send_message(message.chat.id, "Select option:", reply_markup=markup)
'''


def get_main_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(InlineKeyboardButton("Меню"))
    markup.add(InlineKeyboardButton("Поточне замовлення"))
    markup.add(InlineKeyboardButton("Історія замовлень"))
    return markup


def get_categories_markup(categories):
    markup = InlineKeyboardMarkup()
    for category in categories:
        markup.add(
            InlineKeyboardButton(category['name'], callback_data=f"category {category['id']} {category['name']}"))
    return markup


def get_products_markup(products):
    markup = InlineKeyboardMarkup()

    for product in products:
        markup.add(
            InlineKeyboardButton(f"{product['name']}",
                                 callback_data=f"coffee {product['id']} {product['name']}"))
    return markup


def get_sizes_markup(product_id, sizes):
    markup = InlineKeyboardMarkup()
    markup.row_width = len(sizes)
    for size_id in sizes:
        markup.add(
            InlineKeyboardButton(f"{sizes[size_id]['name']}, {sizes[size_id]['price']} грн.",
                                 callback_data=f"addon {product_id} {size_id}"))
    return markup


def get_addons_markup(product_id, size_id, addons):
    markup = InlineKeyboardMarkup()

    for addon in addons:
        markup.add(
            InlineKeyboardButton(f"{addon['name']}, {addon['price']} грн.",
                                 callback_data=f"add_to_cart {product_id} {size_id} {addon['id']}"))
    return markup


def get_cart_markup(cart_content):
    markup = InlineKeyboardMarkup()
    price = 0
    for item in cart_content:
        price += item['price']
        markup.add(InlineKeyboardButton(f"{item['name']} {item['size']} + {item['addon']}, {item['price']} грн.",
                                        callback_data="1"))
        markup.add(InlineKeyboardButton("Додати ще", callback_data=f"coffee {item['product_id']}  {item['name']}"),
                   InlineKeyboardButton("Видалити з замовлення", callback_data=f"remove {item['id']}"))

    markup.add(InlineKeyboardButton("Меню", callback_data="menu"))
    markup.add(InlineKeyboardButton(f"До сплати {price} грн.", callback_data="locations"))
    return markup


def get_added_to_cart_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Меню", callback_data="menu"))
    markup.add(InlineKeyboardButton("Переглянути замовлення", callback_data="current order"))
    return markup


def get_locations_markup(locations):
    markup = InlineKeyboardMarkup()
    for location in locations:
        markup.add(InlineKeyboardButton(f"{location['name']}, {location['address']}",
                                        callback_data=f"location {location['id']},{location['name']},{location['address']}"))
    return markup


def get_pay_markup(order):
    markup = InlineKeyboardMarkup()
    price = 0
    for item in order:
        price += item['price']
        markup.add(InlineKeyboardButton(f"{item['name']} {item['size']} + {item['addon']}, {item['price']} грн.",
                                        callback_data="1"))
    markup.add(InlineKeyboardButton(f"До сплати {price} грн.", callback_data="pay"))
    return markup


def get_orders_markup(orders):
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    for order in orders:
        markup.add(InlineKeyboardButton(
            f"{'✅' if (order['paid']) else '❌'} {datetime.fromisoformat(order['created_on']).strftime('%Y-%m-%d %H:%M')} - {order['price']} грн.",
            callback_data='1'), InlineKeyboardButton("🔁", callback_data=f"repeat {order['id']}"))
    return markup


@bot.message_handler(commands=['start'])
async def register(message):
    data = {
        "user_id": message.from_user.id,
        "first_name": message.from_user.first_name,
        "username": message.from_user.username
    }

    with httpx.Client() as client:
        resp = client.post(API_URL + "clients", data=data)

    await bot.send_message(data['user_id'], start_message, reply_markup=get_main_menu_markup())


@bot.message_handler(func=lambda message: message.text in ['Меню'])
async def main_menu_handler(message):
    categories = await get_categories()
    await bot.send_message(message.chat.id, "Виберіть категорію:", reply_markup=get_categories_markup(categories))


@bot.callback_query_handler(func=lambda callback_query: callback_query.data in ["menu"])
async def main_menu_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    categories = await get_categories()
    await bot.send_message(callback_query.from_user.id, "Виберіть категорію:",
                           reply_markup=get_categories_markup(categories))


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith('category'))
async def category_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    data = callback_query.data.split(' ')[1:]
    category_id = data[0]
    category_name = data[1]
    products = await get_products(category_id)
    await bot.send_message(callback_query.from_user.id, category_name, reply_markup=get_products_markup(products))


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith("coffee"))
async def product_callback1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    product_id = callback_query.data.split(' ')[1]
    product = callback_query.data.split(' ')[2]

    sizes = get_product_sizes(product_id)

    await bot.send_message(callback_query.from_user.id, f'Ви вибрали {product}, виберіть розмір:',
                           reply_markup=get_sizes_markup(product_id, sizes))


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith("addon"))
async def product_callback1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    data = callback_query.data.split(' ')[1:]
    product_id = data[0]
    size_id = data[1]

    addons = await get_addons()

    await bot.send_message(callback_query.from_user.id, 'Бажаєте додаток?',
                           reply_markup=get_addons_markup(product_id, size_id, addons))


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith("add_to_cart"))
async def product_callback2(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    data = callback_query.data.split(" ")[1:]
    user_id = callback_query.from_user.id
    product_id = data[0]
    size_id = data[1]
    addon_id = data[2]

    await add_to_cart(user_id, product_id, size_id, addon_id)

    cart_content = await get_cart_content(callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, 'Додано в замовлення',
                           reply_markup=get_cart_markup(cart_content))


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith("copy"))
async def copy_in_cart_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    data = callback_query.data.split(" ")[1:]
    product_id = data[0]
    await copy_product_in_cart(callback_query.from_user.id, product_id)
    await cart_callback(callback_query)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith("remove"))
async def remove_from_cart_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    data = callback_query.data.split(" ")[1:]
    product_id = data[0]
    await remove_from_cart(callback_query.from_user.id, product_id)
    await cart_callback(callback_query)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'locations')
async def get_locations_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    locations = await get_locations()
    await bot.send_message(callback_query.from_user.id, "Виберіть локацію:",
                           reply_markup=get_locations_markup(locations))


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith('location'))
async def set_location_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    data = callback_query.data.split(',')
    location_id = data[0].split(' ')[1].strip()
    location_name = data[1].strip()
    location_address = data[2].strip()
    await set_location(callback_query.from_user.id, location_id)
    order = await get_cart_content(callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, f"Ви вибрали {location_name}",
                           reply_markup=get_pay_markup(order))


@bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'pay')
async def pay_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await make_order(callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, "Payment url")
    await bot.send_message(callback_query.from_user.id,
                           "Статус оплати вашого замовлення ви можете перевірити в історії замовлень")


@bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'current order')
async def cart_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    cart_content = await get_cart_content(callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, "Ваше замовлення:", reply_markup=get_cart_markup(cart_content))


@bot.message_handler(func=lambda message: message.text in ["Поточне замовлення"])
async def cart_handler(message):
    cart_content = await get_cart_content(message.chat.id)
    await bot.send_message(message.chat.id, "Ваше замовлення:", reply_markup=get_cart_markup(cart_content))


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith('repeat'))
async def order_repeat_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    data = callback_query.data.split(' ')[1:]
    order_id = data[0]
    print('hi')

    cart_content = await add_order_to_cart(callback_query.from_user.id, order_id)
    await bot.send_message(callback_query.from_user.id, "Ваше замовлення:", reply_markup=get_cart_markup(cart_content))


@bot.message_handler(func=lambda message: message.text in ["Історія замовлень"])
async def orders_handler(message):
    orders = await get_order_history(message.chat.id)
    await bot.send_message(message.chat.id, "Історія замовлень:", reply_markup=get_orders_markup(orders))


async def get_categories():
    with httpx.Client() as client:
        resp = client.request("GET", API_URL + "categories")
        print(resp.text)
        return resp.json()


async def get_products(category_id):
    with httpx.Client() as client:
        params = {
            "category_id": category_id
        }
        resp = client.request("GET", API_URL + "products", params=params)
        return resp.json()


async def get_addons():
    with httpx.Client() as session:
        resp = session.request("GET", API_URL + "addons")
        return resp.json()


def get_product_sizes(product_id):
    with httpx.Client() as session:
        resp = session.request("GET", API_URL + f"products/{product_id}/sizes")
        return resp.json()


async def get_locations():
    with httpx.Client() as session:
        resp = session.request("GET", API_URL + "locations")
        return resp.json()


async def set_location(user_id, location_id):
    with httpx.Client() as session:
        resp = session.request("POST", API_URL + f"clients/{user_id}/location")
        return resp.json()


async def get_client_orders(user_id):
    with httpx.Client() as client:
        resp = client.request("GET", API_URL + f"clients/{user_id}/orders")
        return resp.text


async def get_coffee_image(url):
    resp = urllib3.request("GET", API_URL + url)
    return resp.data


async def add_to_cart(user_id, product_id, size_id, addon_id):
    with httpx.Client() as session:
        data = {
            "user_id": user_id,
            "product_id": product_id,
            "size_id": size_id,
            "addon_id": addon_id
        }
        resp = session.request("POST", API_URL + f'clients/{user_id}/cart', data=data)
        return resp.json()


async def copy_product_in_cart(user_id, product_id):
    with httpx.Client() as session:
        params = {
            "product_id": product_id
        }
        resp = session.request("DELETE", API_URL + f'clients/{user_id}/cart', params=params)
        return resp.json()


async def remove_from_cart(user_id, product_id):
    with httpx.Client() as session:
        params = {
            "product_id": product_id
        }
        resp = session.request("DELETE", API_URL + f'clients/{user_id}/cart', params=params)
        return resp.json()


async def add_order_to_cart(user_id, order_id):
    with httpx.Client() as session:
        data = {
            "order_id": order_id
        }
        resp = session.request("POST", API_URL + f'clients/{user_id}/cart', data=data)
        return resp.json()


async def get_cart_content(user_id):
    with httpx.Client() as session:
        resp = session.request("GET", API_URL + f"clients/{user_id}/cart")
        return resp.json()


async def make_order(user_id):
    with httpx.Client() as session:
        resp = session.request("POST", API_URL + f"clients/{user_id}/orders")
        return resp.json()


async def get_order_history(user_id):
    with httpx.Client() as session:
        resp = session.request("GET", API_URL + f"clients/{user_id}/orders")
        return resp.json()


if __name__ == '__main__':
    '''
    data = {'user_id': 333588062, 'first_name': 'Xsayros', 'username': 'Xsayr'}
    # ssl_context = httpx.create_ssl_context()
    # ssl_context.options ^= ssl.OP_NO_TLSv1  # Enable TLS 1.0 back
    with httpx.Client() as client:
        resp = client.post(API_URL + "clients", data=data)
        print(resp.text)
    '''
    asyncio.run(bot.infinity_polling())
