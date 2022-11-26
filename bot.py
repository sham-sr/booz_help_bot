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
            "/butt - попки"
            )
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


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await message.answer(f"Не понимаю тебя иди нах:\n"
                         f"{message.text}\n"
                         f"Набери /help")


async def on_shutdown(dp):
    await bot.delete_webhook()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=on_shutdown, loop=loop)
