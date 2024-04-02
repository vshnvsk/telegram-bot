import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

import database
import my_keyboards as kb

user_data = {}
user_group = {}
user_select = {}
user_info = {}
name_subject = 'name'

load_dotenv()
key = os.getenv('API_token')

bot = Bot(token=key)
dp = Dispatcher()


async def on_startup(_):
    await database.db_connect()
    print("Connect")


#-------------------------------For the start button and subgroup selection------------------------------

@dp.message(Command("start"))
async def command_start_handler(message: Message):
    user_select[message.from_user.id] = []
    user_data[message.from_user.id] = 0
    await message.answer_sticker(sticker="CAACAgIAAxkBAAEL0ORmCBKDjapEhTrTGNJJA-eSAtOFtwAChwIAAladvQpC7XQrQFfQkDQE")
    await message.answer(f"Привіт, {message.from_user.full_name}! Вибери свою підгрупу:",
                         reply_markup=kb.start())


@dp.callback_query(F.data.startswith("group_"))
async def callback_group(callback: CallbackQuery):
    with suppress(TelegramBadRequest):
        group = callback.data.split("_")[1]

        user_group[callback.from_user.id] = {
            "group_": group
        }

        await callback.message.answer(f"Вибрано {group}")

        print(user_group)

        ordinary_subject = database.get_ordinary_subject(group)

        if not ordinary_subject:
            await callback.message.answer("Nothing(")
            return await callback.answer()

        message_text = f"Перелік основних дисциплін:\n"
        for row in ordinary_subject:
            message_text += f"- {row[0]}\n"

        await callback.message.answer(message_text)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Виберіть додаткові предмети:",
                                      reply_markup=kb.get_keyboard_select(False))


#--------------------------------For the selection button(elective subject)------------------------------

@dp.message(Command("subjects"))
async def start_elective_subject(message: Message):
    user_data[message.from_user.id] = 0
    await message.answer("Виберіть додаткові предмети:",
                         reply_markup=kb.get_keyboard_select(False))


async def update_num_text(message: Message, num_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Кількість вибраних предметів: {num_value}",
            reply_markup=kb.get_keyboard_select(False)
        )


async def delete_button(message: Message, callback_data: str):
    keyboard = message.reply_markup

    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == callback_data:
                row.remove(button)

    await message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query(F.data.startswith("select_"))
async def callbacks_selected_subject(callback: CallbackQuery):
    with suppress(TelegramBadRequest):
        user_value = user_data.get(callback.from_user.id, 0)
        action = callback.data.split("_")[1]
        subject = callback.data.split("_")[1]

        if subject != "finish" and subject != "reset":
            sub = {name_subject: subject}
            if callback.from_user.id not in user_select:
                user_select[callback.from_user.id] = []
            if len(user_select[callback.from_user.id]) < 3:
                user_select[callback.from_user.id].append(sub)
            else:
                await callback.message.answer("Ви вже обрали максимальну кількість предметів❗")
                return

        elif subject == "reset":
            user_select[callback.from_user.id] = []

        print(user_select)

        all_subject = []

        if action == "finish":
            if len(user_select[callback.from_user.id]) < 3:
                await callback.message.answer("Ви обрали недостатню кількість предметів❗")
                return
            else:
                await callback.message.edit_text(f"Ви вибрали: {user_value} предмет(-а)")

                for values_for_user in user_select.values():
                    for value in values_for_user:
                        selected_subject = database.get_selected_subject(value['name'])
                        all_subject += selected_subject

                if not selected_subject:
                    await callback.message.answer("Nothing(")
                    return await callback.answer()

                message_text = f"Перелік вибіркових дисциплін:\n"
                for row in all_subject:
                    message_text += f"- {row[0]}\n"

                await callback.message.answer(message_text)
                return

        if action == "reset":
            user_data[callback.from_user.id] = 0
            await update_num_text(callback.message, 0)
            await callback.answer()
            await callback.message.edit_reply_markup(reply_markup=kb.get_keyboard_select(False))
            return

        user_data[callback.from_user.id] = user_value + 1
        await update_num_text(callback.message, user_value + 1)
        await delete_button(callback.message, callback.data)
        await callback.answer()
        return


#-----------------------------For the schedule------------------------------

@dp.message(Command("schedule"))
async def start_schedule(message: Message):
    await message.answer("Ваш розклад:",
                         reply_markup=kb.get_all_schedule())


@dp.callback_query(F.data == "schedule")
async def callback_schedule(callback: CallbackQuery):
    with suppress(TelegramBadRequest):
        for user_id in user_group.keys():
            if user_id in user_select:
                user_info[user_id] = {'group_': user_group[user_id]['group_'],
                                      'selected subject': user_select[user_id]}

        print(user_info)

        await callback.answer()


async def main() -> None:
    await on_startup(None)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())