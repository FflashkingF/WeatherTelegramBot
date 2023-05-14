import logging
import requests
import config_
import keyboards_
import json
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


def get_url_by_location(location: str) -> str: #domen to constant
    return f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={config_.WEATHER_API}&units=metric'


def get_url_by_lat_lon(lat: float, lon: float):
    return f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={config_.WEATHER_API}&units=metric'


async def try_answer(message: types.Message, url: str, location: str, state: FSMContext) -> None:
    response = requests.get(url)

    print(response.status_code)
    if response.status_code == 200: #
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
        message_text = f"Sorry, I couldn't find weather information for {location}.\n" + \
            "Please try again."
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
    url = "https://api.thecatapi.com/v1/images/search"
    response = requests.get(url)
    print(response.status_code)
    if response.status_code == 200: 
        cat_data = response.json()
        cat_url : str = cat_data[0]['url']
        cat_response = requests.get(cat_url)
        cat_name : str = cat_url.split('/')[-1]
        rash : str = cat_name.split('.')[-1]
        print(cat_url, cat_name)
        full_path = pathlib.Path(__file__).parent.resolve()/('cat.' + rash)
        print(full_path)
        with open(full_path, "wb") as cat:
            cat.write(cat_response.content)
        cat = open(full_path, "rb")
        if rash == 'gif':
            await bot.send_animation(message.chat.id, animation=cat)
        else:
            await bot.send_photo(message.chat.id, photo=cat)
        cat.close()
        os.remove(full_path)

    else:
        message_text = "Sorry, i can't find a cat."
        await message.answer(message_text,  reply_markup=keyboards_.start_kb)

@dp.message_handler()  # anything or help, start
async def help_handler(message: types.Message):
    message_text = 'Instruction\n' + \
        '/cats to get picture with cat\n' + \
        '/Write_location to ask weather in location which you want\n' + \
        f'Press button "{json.loads(keyboards_.button_location.as_json())["text"]}" to see weather ' +  \
        'in your own location(you also can drop custom location)\n' + \
        '/cancel to return in /start\n' + \
        '/stop to stop bot'
    await message.reply(message_text, reply_markup=keyboards_.start_kb)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
