import asyncio
from aiogram import executor
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.builtin import CommandHelp, CommandStart, Command
from aiogram.types import CallbackQuery, InputFile
from aiogram.dispatcher import FSMContext
import random
from ImageParser import YandexImage
from aiogram.types import InputFile
from bot_openai import ai_answers
from ya_api import ya_translate
from markdownify import markdownify
from html_strip import strip_tags
import requests
from pathlib import Path
import os

parser = YandexImage()

boobs_l = ['красивые сиськи',
           'маленькие сиськи',
           'огромные сиськи',
           'замечатеельные сиськи',
           'соски торчком',
           'сиськи в кружевном белье',
           'черный сиськи',
           'азиатские сиськи',
           'сиськи',
           'крем сиськи']
butt_l = ['попка',
          'попка бикини',
          'попка в кружевном',
          'оргомная попка',
          'азиатская попка',
          'афро попка',
          'голая попка',
          'попка 18+',
          'попка в масле']


loop = asyncio.get_event_loop()
bot = Bot(token="5607448461:AAFfZ847ENr3Jfmdjh9VXDi8fBNqWCXUeLE",
          parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, loop, storage=storage)


@dp.message_handler(Command('ural'), state="*")
async def bot_ural(message: types.Message, state: FSMContext):
    lines = open('/home/jovyan/work/booze_help_bot/ural_word.txt').read().splitlines()
    myline = random.choice(lines)
    await message.answer(myline)


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Список команд: ",
            "/start - начать строчить",
            "/ural - учи уральский говор чёмор",
            "/boobs - сиськи",
            "/butt - попки",            
            "если набирать без команд отвечать будет ИИ \n начни набор с *eng результат вернется на английском")
    await message.answer("\n".join(text))


@dp.message_handler(CommandStart())
async def bot_start_for_reg_user(message: types.Message):
    await message.answer(f"Здарова - заебал, {message.from_user.full_name}! Начни с /help .")


@dp.message_handler(Command('boobs'), state="*")
async def bot_boobs(message: types.Message, state: FSMContext):
    boobs = parser.search(random.choice(boobs_l))
    if len(boobs) > 0:
        await message.answer_photo(InputFile.from_url(random.choice(boobs).preview.url))
    else:
        print('ищу в рамблер')
        boobs = parser.search(random.choice(boobs_l), sources='rambler')
        await message.answer_photo(InputFile.from_url(random.choice(boobs)))


@dp.message_handler(Command('butt'), state="*")
async def bot_butt(message: types.Message, state: FSMContext):
    butt = parser.search(random.choice(butt_l))
    if len(butt) > 0:
        await message.answer_photo(InputFile.from_url(random.choice(butt).preview.url))
    else:
        print('ищу в рамблер')
        butt = parser.search(random.choice(butt_l), sources='rambler')
        await message.answer_photo(InputFile.from_url(random.choice(butt)))


@dp.message_handler(state=None, content_types=types.ContentTypes.TEXT)
async def bot_echo(message: types.Message):
    print(f'user:{message.from_user.full_name}, text:{message.text}')
    if message.text.startswith('*loc'):
        text_in = message.text.replace('*loc', '',1) 
    else:
        text_in = ya_translate(message.text, target_language='en')         
    if text_in is not None:
        try:
            ai_text = ai_answers(os.getenv("ORGANIZATION"),
                            os.getenv("OPENAI_API_KEY"),
                            prompt=text_in) 
        except:
             await message.answer('Что то пошло не так c мозгом ИИ')             
        if not message.text.startswith('*eng'):
            ai_text = ya_translate(strip_tags(ai_text)).replace('*eng', '',1)
            if ai_text is None:
                await message.answer('Что то пошло не так c преводом на RU!')
            else:
                await message.answer(strip_tags(ai_text)) 
        else:
            await message.answer(strip_tags(ai_text))            
    else:
        await message.answer('Что то пошло не так c преводом на EN!')
    
@dp.message_handler(content_types=[
    types.ContentType.VOICE,
    types.ContentType.AUDIO
    ]
)
async def voice_message_handler(message: types.Message):
    """
    Обработчик на получение голосового и аудио сообщения.
    """
    if message.content_type == types.ContentType.VOICE:
        file_id = message.voice.file_id
    elif message.content_type == types.ContentType.AUDIO:
        file_id = message.audio.file_id
    else:
        await message.reply("Формат документа не поддерживается")
        return

    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"{file_id}.tmp")
    await bot.download_file(file_path, destination=file_on_disk)
    await message.reply("Аудио получено")

    # Convert the audio file to text using Yandex Speech Kit
    with open(file_path, "rb") as file:
        audio_data = file.read()

    url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
    headers = {
        "Authorization": f'Api-Key {os.getenv("YA_API_KEY")}',
        "Content-Type": "audio/x-pcm;bit=16;rate=16000"
    }

    response = requests.post(url, headers=headers, data=audio_data)

    if response.ok:
        # Extract the text from the response
        result = response.json().get("result")
        if result:
            # Process the text and generate a response
            reply = generate_response(result)
            await message.reply(reply)
        else:
            await message.reply("Sorry, I couldn't recognize the speech.")
    else:
        await message.reply("Oops! Something went wrong.")

    os.remove(file_on_disk)  # Удаление временного файла


async def on_shutdown(dp):
    await bot.delete_webhook()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=on_shutdown, loop=loop)
