from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

button_weather = KeyboardButton('/Write_location')
button_location = KeyboardButton('Send location 🗺️', request_location=True)
button_cats = KeyboardButton('/cats')
start_kb = ReplyKeyboardMarkup(resize_keyboard=True).row(button_weather, button_location).row(button_cats)