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
name_subject = 'name'

load_dotenv()
key = os.getenv('API_token')

bot = Bot(token=key)
dp = Dispatcher()


async def on_startup(_):
    await database.db_connect()
    print("Connect")


# -------------------------------For the start button and subgroup selection------------------------------

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
        local_user_group = user_group.get(callback.from_user.id, {})

        local_user_group["group"] = group
        user_group[callback.from_user.id] = local_user_group

        await bot.send_message(chat_id=callback.from_user.id,
                               text=f"Вибрано {group}")

        print(local_user_group)

        ordinary_subject = database.get_ordinary_subject(group)

        if not ordinary_subject:
            await callback.message.answer("Nothing(")
            return await callback.answer()

        message_text = f"Перелік основних дисциплін:\n"
        for row in ordinary_subject:
            message_text += f"- {row[0]}\n"

        print(f"User ID: {callback.from_user.id}, Group: {group}")

        await bot.send_message(chat_id=callback.from_user.id,
                               text=message_text)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Виберіть додаткові предмети:",
                                      reply_markup=kb.get_keyboard_select(False))


# --------------------------------For the selection button(elective subject)------------------------------

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

        local_user_select = user_select.get(callback.from_user.id, [])

        if subject != "finish" and subject != "reset":
            sub = {'name': subject}
            if len(local_user_select) < 3:
                local_user_select.append(sub)
            else:
                await bot.send_message(chat_id=callback.from_user.id,
                                       text="Ви вже обрали максимальну кількість предметів❗")
                return

        elif subject == "reset":
            local_user_select = []

        print(local_user_select)

        all_subject = []

        if action == "finish":
            if len(local_user_select) < 3:
                await bot.send_message(chat_id=callback.from_user.id,
                                       text="Ви обрали недостатню кількість предметів❗")
                return
            else:
                await callback.message.edit_text(f"Ви вибрали: {user_value} предмета")

                for value in local_user_select:
                    selected_subject = database.get_selected_subject(value['name'])
                    all_subject += selected_subject

                if not all_subject:
                    await callback.message.answer("Nothing(")
                    return await callback.answer()

                message_text = f"Перелік вибіркових дисциплін:\n"
                for row in all_subject:
                    message_text += f"- {row[0]}\n"

                await bot.send_message(chat_id=callback.from_user.id,
                                       text=message_text)
                await callback.message.answer("Ваш розклад:",
                                              reply_markup=kb.get_all_schedule())
                return

        if action == "reset":
            user_select[callback.from_user.id] = []
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


# -----------------------------For the schedule------------------------------

@dp.message(Command("schedule"))
async def start_schedule(message: Message):
    await message.answer("Ваш розклад:",
                         reply_markup=kb.get_all_schedule())


@dp.callback_query(F.data == "schedule")
async def callback_schedule(callback: CallbackQuery):
    with suppress(TelegramBadRequest):
        # global user_group, user_select

        local_user_group = user_group.get(callback.from_user.id, {})
        local_user_select = user_select.get(callback.from_user.id, [])

        info_group = ""
        info_select = []

        for i in local_user_group.values():
            # for j in i.values():
            info_group = i

        for i in local_user_select:
            for j in i.values():
                info_select.append(j)

        info_select_tuple = tuple(info_select)

        # combined_data = {}
        #
        # for user_id, group_data in user_group.items():
        #     if user_id in user_select:
        #         selected_subjects = user_select[user_id]
        #         combined_data[user_id] = {'group': group_data['group'], 'selected_subjects': selected_subjects}
        #
        # print(combined_data)

        print(user_group)
        print(user_select)
        print(info_group)
        print(info_select_tuple)

        schedule = database.get_all_subject_second_week(info_group, info_select_tuple)

        # for value in local_user_select:
        #     selected_subject = database.get_selected_subject(value['name'])
        #     all_subject += selected_subject
        #
        # if not all_subject:
        #     await callback.message.answer("Nothing(")
        #     return await callback.answer()
        #
        # message_text = f"Перелік вибіркових дисциплін:\n"
        # for row in all_subject:
        #     message_text += f"- {row[0]}\n"

        print(schedule)

        message_text = f"Розклад:\n"
        for row in schedule:
            message_text += f"- {row[2]}\n"

        await bot.send_message(chat_id=callback.from_user.id,
                               text=message_text)
        await callback.answer()


async def main() -> None:
    await on_startup(None)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())