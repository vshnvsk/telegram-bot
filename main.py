import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

from aiogram import types, Bot, Dispatcher
from aiogram import F
from aiogram.filters.command import Command
from aiogram.types import Message
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

import database
import my_keyboards as kb

user_data = {}

load_dotenv()
key = os.getenv('API_token')

bot = Bot(token=key)
dp = Dispatcher()


async def on_startup(_):
    await database.db_connect()
    print("Connect")

#---------------------For the start button and subgroup selection------------------------------


@dp.message(Command("start"))
async def command_start_handler(message: Message):
    await message.answer_sticker(sticker="CAACAgIAAxkBAAEL0ORmCBKDjapEhTrTGNJJA-eSAtOFtwAChwIAAladvQpC7XQrQFfQkDQE")
    await message.answer(f"Привіт, {message.from_user.full_name}! Вибери свою підгрупу:",
                         reply_markup=kb.start())


@dp.callback_query(F.data.startswith("group_"))
async def callback_group(callback: types.CallbackQuery):
    with suppress(TelegramBadRequest):
        group = callback.data.split("_")[1]
        await callback.message.answer(f"Вибрано {group}")

        ordinary_subject = database.get_ordinary_subject(group)

        if not ordinary_subject:
            await callback.message.answer("Nothing(")
            return await callback.answer()

        message_text = f"Перелік основних дисциплін:\n"
        for row in ordinary_subject:
            message_text += f"- {row[0]}\n"

        await callback.message.answer(message_text)

        await callback.message.edit_reply_markup(reply_markup=None)


#---------------------For the selection button(elective subject)------------------------------


@dp.message(Command("subjects"))
async def elective_subject(message: Message):
    user_data[message.from_user.id] = 0
    await message.answer("Вибіркові предмети: 0",
                         reply_markup=kb.get_keyboard_select())


async def update_num_text(message: Message, num_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Вибіркові предмети: {num_value}",
            reply_markup=kb.get_keyboard_select()
        )


@dp.callback_query(F.data.startswith("select_"))
async def callbacks_selected_subject(callback: types.CallbackQuery):
    user_value = user_data.get(callback.from_user.id, 0)
    action = callback.data.split("_")[1]

    user_data[callback.from_user.id] = user_value + 1
    await update_num_text(callback.message, user_value + 1)

    await delete_button(callback.message, callback.data)

    await callback.answer()

    if action == "finish":
        await callback.message.edit_text(f"Ви вибрали: {user_value}")


async def delete_button(message: Message, callback_data: str):
    keyboard = message.reply_markup

    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == callback_data:
                row.remove(button)

    await message.edit_reply_markup(reply_markup=keyboard)


async def main() -> None:
    await on_startup(None)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())