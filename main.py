import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

from aiogram import types, Bot, Dispatcher
from aiogram import F
from aiogram.filters.command import Command
from aiogram.types import Message

import database
import my_keyboards as kb

load_dotenv()
key = os.getenv('API_token')

bot = Bot(token=key)
dp = Dispatcher()


async def on_startup(_):
    await database.db_connect()
    print("Connect")


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привіт, {message.from_user.full_name}! Вибери свою підгрупу",
                         reply_markup=kb.start())


@dp.message(F.text.lower() == "341а")
async def group_a(message: Message):
    #await database.select_group_a()
    await message.answer("Вибрано 341А")


@dp.message(F.text.lower() == "341б")
async def group_b(message: Message):
    await message.answer("Вибрано 341Б")


@dp.message(F.text.lower() == "341ск")
async def group_short(message: Message):
    await message.answer("Вибрано 341СК")


async def main() -> None:
    await on_startup(None)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())