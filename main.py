import asyncio
from datetime import datetime
import logging
import os
import sys

from aiogram.enums import ParseMode
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import database
import my_keyboards as kb

user_data = {}
user_group = {}
user_select = {}
name_subject = 'name'
get_id = None

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
    global get_id
    get_id = message.from_user.id

    user_select[message.from_user.id] = []
    user_data[message.from_user.id] = 0
    await message.answer_sticker(sticker="CAACAgIAAxkBAAEL0ORmCBKDjapEhTrTGNJJA-eSAtOFtwAChwIAAladvQpC7XQrQFfQkDQE")
    await message.answer(f"Привіт, {message.from_user.full_name}🧑🏻‍🎓! Вибери свою підгрупу:",
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

        message_text = f"Перелік основних дисциплін: 📚\n"
        for row in ordinary_subject:
            message_text += f"- {row[0]}\n"

        print(f"User ID: {callback.from_user.id}, Group: {group}")

        await bot.send_message(chat_id=callback.from_user.id,
                               text=message_text)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Виберіть 3 додаткових предмета:",
                                      reply_markup=kb.get_keyboard_select(False))


# --------------------------------For the selection button(elective subject)------------------------------

@dp.message(Command("subjects"))
async def start_elective_subject(message: Message):
    user_data[message.from_user.id] = 0
    await message.answer("Виберіть 3 додаткових предмета:",
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

                message_text = f"Перелік вибіркових дисциплін: 📚\n"
                for row in all_subject:
                    message_text += f"- {row[0]}\n"

                await bot.send_message(chat_id=callback.from_user.id,
                                       text=message_text)
                await bot.send_message(chat_id=callback.from_user.id, text="📆")
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
        local_user_group = user_group.get(callback.from_user.id, {})
        local_user_select = user_select.get(callback.from_user.id, [])

        info_group = ""
        info_select = []

        for i in local_user_group.values():
            info_group = i

        for i in local_user_select:
            for j in i.values():
                info_select.append(j)

        info_select_tuple = tuple(info_select)

        print(user_group)
        print(user_select)
        print(info_group)
        print(info_select_tuple)

        current_date = datetime.now()
        week_number = current_date.isocalendar()[1]

        if week_number % 2 == 0:
            await bot.send_message(chat_id=callback.from_user.id,
                                   text="Зараз навчання за ІІ-им тижнем")
            schedule = database.get_all_subject_second_week(info_group, info_select_tuple)
        else:
            await bot.send_message(chat_id=callback.from_user.id,
                                   text="Зараз навчання за І-им тижнем")
            schedule = database.get_all_subject_first_week(info_group, info_select_tuple)

        print(schedule)

        previous_weekday = ""
        message_schedule = ""

        for values in schedule:
            weekday = values[0]
            if weekday != previous_weekday:
                if previous_weekday:
                    await bot.send_message(chat_id=callback.from_user.id, text=message_schedule,
                                           parse_mode=ParseMode.HTML)
                    await asyncio.sleep(1)
                message_schedule = f"📆<b>{weekday}:</b>\n➖➖➖➖➖➖➖➖➖➖➖➖\n"
                previous_weekday = weekday
            message_schedule += f"<b>{values[1]}. {values[2]}</b>\n"
            message_schedule += f"     ▫ {values[3]} {values[4]}\n"
            message_schedule += f"     ▫ {values[5]}\n"
            message_schedule += f"     ▫ {values[6]} ауд.\n"
            message_schedule += f"     ▫ {values[7]}-{values[8]}\n"
            message_schedule += f"     ▫ {values[9]}\n"

        await bot.send_message(chat_id=callback.from_user.id, text=message_schedule, parse_mode=ParseMode.HTML)
        await asyncio.sleep(1)

        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Додаткова інформація:", reply_markup=kb.get_info())
        await callback.answer()


# -----------------------------For the notification------------------------------

async def send_notification():
    global get_id
    current_datetime = datetime.now()

    if get_id is not None:
        if current_datetime.weekday() == 6 and current_datetime.hour >= 20:
            await bot.send_message(chat_id=get_id,
                                   text=f"Привіт! Ось ваш розклад на наступний тиждень:",
                                   reply_markup=kb.get_all_schedule())
    else:
        print("I don't know anyone(")


# --------------------------For other options---------------------------
@dp.message(F.text.lower() == "коли заліки?")
async def when_session(message: Message):
    await message.reply("🔹З 15 по 31 травня")


@dp.message(F.text.lower() == "коли сесія?")
async def when_test(message: Message):
    await message.reply("🔸З 1 по 19 червня")


@dp.message(F.text.lower() == "скинути налаштування❌")
async def reset_settings(message: Message):
    global get_id
    get_id = None
    get_id = message.from_user.id

    user_select[message.from_user.id] = []
    user_data[message.from_user.id] = 0
    await message.answer_sticker(sticker="CAACAgIAAxkBAAEL5wFmGWPhnFAzYtZh_Lw0EnOCkfGCrgACXgAD5KDOB11SuKzKYMdkNAQ")
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Привіт знову, {message.from_user.full_name}🧑🏻‍🎓! Вибери свою підгрупу:",
                           reply_markup=kb.start())


async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_notification, "cron", day_of_week="sun", hour=20, minute=0)
    scheduler.start()

    await on_startup(None)
    await dp.start_polling(bot, skip_updates=True),

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())