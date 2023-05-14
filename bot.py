import logging
import requests
import config_
import keyboards_
import url_names_
import texts_
import status_codes_
import json
import uuid
import pathlib
import os
from pprint import pprint
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config_.BOT_API)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(state='*', commands=['stop'])
async def send_welcome(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await message.reply('Goodbye', reply_markup=keyboards_.ReplyKeyboardRemove())


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await message.reply('Cancelled', reply_markup=keyboards_.start_kb)


class Input_location(StatesGroup):
    location = State()  # Will be represented in storage as 'Form:name'


@dp.message_handler(commands=['Write_location'])
async def input_location_handler(message: types.Message):
    await Input_location.location.set()
    await message.answer("Please write location.")


def get_url_by_location(location: str) -> str:  # domen to constant
    return url_names_.WEATHER_BY_NAME.format(location_name=location, weather_api=config_.WEATHER_API)


def get_url_by_lat_lon(lat: float, lon: float):
    return url_names_.WEATHER_BY_LAT_LON.format(lat=lat, lon=lon, weather_api=config_.WEATHER_API)


async def try_answer(message: types.Message, url: str, location: str, state: FSMContext) -> None:
    response = requests.get(url)

    print(response.status_code)
    if response.status_code == status_codes_.RESPONSE_GOOD:
        # print(response)
        weather_data = response.json()
        # print(weather_data)
        pprint(weather_data)
        temperature = weather_data['main']['temp']
        temperature_feel = weather_data['main']['feels_like']
        description: str = weather_data['weather'][0]['description']
        wind_speed = weather_data['wind']['speed']
        location = weather_data['name']
        country = weather_data['sys']['country']
        message_text = f'Temperature in {country}, {location} is {temperature:0.1f}°C\n' + \
            f'It is feels like {temperature_feel:0.1f}°C\n' + \
            f'{description.capitalize()}\n' + \
            f'Wind speed is {wind_speed:0.1f}m/s'
        await state.finish()
    else:
        message_text = texts_.wrong_location.format(location=location)
    await message.answer(message_text,  reply_markup=keyboards_.start_kb)


@dp.message_handler(content_types=['location'], state='*')
async def handle_location(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    url = get_url_by_lat_lon(lat, lon)
    print(url)

    await try_answer(message, url, f"lat: {lat}, lon: {lon}", state)


@dp.message_handler(state=Input_location.location)
async def process_input_location(message: types.Message, state: FSMContext):
    location = message.text
    location = location.strip()
    location = ' '.join(location.split(' '))
    url = get_url_by_location(location)
    print(url)

    await try_answer(message, url, location, state)


@dp.message_handler(commands=['cats'])
async def input_location_handler(message: types.Message) -> None:
    response = requests.get(url_names_.CATS)
    print(response.status_code)
    if response.status_code == status_codes_.RESPONSE_GOOD:
        cat_data = response.json()
        cat_url: str = cat_data[0]['url']
        cat_response = requests.get(cat_url)
        cat_name: str = cat_url.split('/')[-1]
        rash: str = cat_name.split('.')[-1]
        print(cat_url, cat_name)
        unique_filename = str(uuid.uuid4())
        full_path = pathlib.Path(__file__).parent.resolve()/(unique_filename + cat_name)
        print(full_path)
        with open(full_path, "wb") as cat:
            cat.write(cat_response.content)

        with open(full_path, "rb") as cat:
            if rash == 'gif':
                await bot.send_animation(message.chat.id, animation=cat)
            else:
                await bot.send_photo(message.chat.id, photo=cat)
            os.remove(full_path)

    else:
        await message.answer(texts_.sorry_by_cats,  reply_markup=keyboards_.start_kb)


@dp.message_handler()  # anything or help, start
async def help_handler(message: types.Message):
    await message.reply(texts_.main, reply_markup=keyboards_.start_kb)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
