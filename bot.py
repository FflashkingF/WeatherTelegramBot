import logging
import requests
import config_
import keyboards_
from pprint import pprint
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config_.BOT_API)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply('Hello', reply_markup=keyboards_.start_kb)


@dp.message_handler(commands=['stop'])
async def send_welcome(message: types.Message):
    await message.reply('Goodbye')


class Input_location(StatesGroup):
    location = State()  # Will be represented in storage as 'Form:name'


@dp.message_handler(commands=['Write_location'])
async def input_location_handler(message: types.Message):
    await Input_location.location.set()
    await message.answer("Please write location.")


def get_url_by_location(location: str) -> str:
    return f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={config_.WEATHER_API}&units=metric'


def get_url_by_lat_lon(lat: float, lon: float):
    return f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={config_.WEATHER_API}&units=metric'


async def try_answer(message: types.Message, url: str, location: str, state: FSMContext) -> None:
    response = requests.get(url)

    print(response.status_code)
    if response.status_code == 200:
        #print(response)
        weather_data = response.json()
        #print(weather_data)
        pprint(weather_data)
        temperature = weather_data['main']['temp']
        temperature_feel = weather_data['main']['feels_like']
        description : str = weather_data['weather'][0]['description']
        wind_speed = weather_data['wind']['speed']
        location = weather_data['name']
        country = weather_data['sys']['country']
        message_text = f'Temperature in {country}, {location} is {temperature:0.1f}°C\n' + \
            f'It is feels like {temperature_feel:0.1f}°C\n' + \
            f'{description.capitalize()}\n' + \
            f'Wind speed is {wind_speed:0.1f}m/s'
        success = True
        await state.finish()
    else:
        success = False
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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
