import requests
import config_
from aiogram import Bot, Dispatcher, types, executor

bot = Bot(token=config_.BOT_API)

dp = Dispatcher(bot)

@dp.message_handler(commands=['start']) 
async def send_welcome(message: types.Message):
   await message.reply('Hello') 

@dp.message_handler(commands=['start']) 
async def send_welcome(message: types.Message):
   await message.reply('Goodbye') 

@dp.message_handler(commands=['weather'])
async def weather_command_handler(message: types.Message):
    location = message.text.split(' ', 1)[-1]
    
    url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={config_.WEATHER_API}&units=metric'
    response = requests.get(url)

    print(response.status_code)

    if response.status_code == 200:
        weather_data = response.json()
        temperature = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        message_text = f'The temperature in {location} is {temperature}°C and the weather is {description}.'
    else:
        message_text = f"Sorry, I couldn't find weather information for {location}."

    await bot.send_message(chat_id=message.chat.id, text=message_text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
