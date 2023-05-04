from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
  
button_weather = KeyboardButton('/Write_location')
button_location = KeyboardButton('Send location 🗺️', request_location=True)
start_kb = ReplyKeyboardMarkup(resize_keyboard=True).row(button_weather, button_location)