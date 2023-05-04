import requests
import config_
from pprint import pprint
from aiogram import Bot, Dispatcher, types, executor

bot = Bot(token=config_.BOT_API)

dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply('Hello')


@dp.message_handler(commands=['stop'])
async def send_welcome(message: types.Message):
    await message.reply('Goodbye')


@dp.message_handler(commands=['weather'])
async def weather_command_handler(message: types.Message):
    location = message.text.split(' ', 1)[-1]
    location = location.strip()
    location = ' '.join(location.split(' '))
    print(location)
    if location :
        url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={config_.WEATHER_API}&units=metric'
        response = requests.get(url)

        print(response.status_code)

        if response.status_code == 200:
            print(response)
            weather_data = response.json()
            print(weather_data)
            pprint(weather_data)
            temperature = weather_data['main']['temp']
            temperature_feel = weather_data['main']['feels_like']
            description = weather_data['weather'][0]['description']
            wind_speed = weather_data['wind']['speed']
            location = weather_data['name']
            message_text = f'Temperature in {location} is {temperature:0.1f}°C\n' + \
                f'It is feels like {temperature_feel:0.1f}°C\n' + \
                f'Weather is {description}\n' + \
                f'Wind speed is {wind_speed:0.1f}m/s'
        else:
            message_text = f"Sorry, I couldn't find weather information for {location}."
    else:
        message_text = 'Your location is empty'
    await message.answer(message_text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
