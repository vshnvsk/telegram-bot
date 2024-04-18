import asyncio
from datetime import datetime
import calendar
import logging
import os
import sys
import random

from aiogram.enums import ParseMode
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.methods import DeleteWebhook

import database
import my_keyboards as kb

user_states = {}
user_data = {}
user_group = {}
user_select = {}
name_subject = 'name'
get_id = None

sticker_list = [
    'CAACAgIAAxkBAAEL0ORmCBKDjapEhTrTGNJJA-eSAtOFtwAChwIAAladvQpC7XQrQFfQkDQE',
    'CAACAgIAAxkBAAEL5wFmGWPhnFAzYtZh_Lw0EnOCkfGCrgACXgAD5KDOB11SuKzKYMdkNAQ',
    'CAACAgIAAxkBAAEL7lFmH7u08yZu_zy_-L_fLAvWJKL39wAC9wEAAhZCawo59nBvtGN_xDQE',
    'CAACAgIAAxkBAAEL7lRmH7wOblDDtkW9P_SEEW1Bgt4AATkAAgUAA8A2TxP5al-agmtNdTQE',
    'CAACAgIAAxkBAAEL7lVmH7wOF7r1UcKIMa7vS8dkMzk8ygACHgkAAhhC7gj5WNnuHSGcITQE',
    'CAACAgIAAxkBAAEL7lZmH7wOXAAB4KeT1r2K0jY5Ea2o-0oAAj8AAyRxYhovqlPpGH07ZzQE',
    'CAACAgIAAxkBAAEL7ldmH7wOWk2oHZGVo-X7G4siCVQvvgACTwADrWW8FGuRHI2HrK-TNAQ',
    'CAACAgIAAxkBAAEL7lhmH7wOmtjEdNJeFyYo8SwMWrTX_QACjgADFkJrCr6khn1tfi1cNAQ'
]

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

    random_sticker = random.choice(sticker_list)

    await message.answer_sticker(sticker=random_sticker)
    await message.answer(f"Привіт, {message.from_user.full_name}🧑🏻‍🎓! Вибери свою підгрупу:",
                         reply_markup=kb.start())


@dp.callback_query(F.data.startswith("group_"))
async def callback_group(callback: CallbackQuery):
    with suppress(TelegramBadRequest):
        group = callback.data.split("_")[1]
        local_user_group = user_group.get(callback.from_user.id, {})

        local_user_group["group"] = group
        user_group[callback.from_user.id] = local_user_group

        await callback.message.edit_text(text=f"<b>Вибрано:</b> {group}",
                                         parse_mode=ParseMode.HTML)

        print(local_user_group)

        ordinary_subject = database.get_ordinary_subject(group)

        if not ordinary_subject:
            await callback.message.answer("Nothing(")
            return await callback.answer()

        message_text = f"📚 <b>Перелік основних дисциплін:</b>\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️️\n"
        for row in ordinary_subject:
            message_text += f"   ▫️ {row[0]}\n"

        print(f"User ID: {callback.from_user.id}, Group: {group}")

        await bot.send_message(chat_id=callback.from_user.id,
                               text=message_text,
                               parse_mode=ParseMode.HTML)
        await callback.message.answer(text="<b>Вибери 3️⃣ додаткових предмета:</b>",
                                      reply_markup=kb.get_keyboard_select(False),
                                      parse_mode=ParseMode.HTML)


# --------------------------------For the selection button(elective subject)------------------------------
async def update_num_text(message: Message, num_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            text=f"<b>Кількість вибраних предметів:</b> {num_value}",
            reply_markup=kb.get_keyboard_select(False),
            parse_mode=ParseMode.HTML
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
                                       text="Ти вже обрав максимальну кількість предметів❗")
                return

        elif subject == "reset":
            local_user_select = []

        print(local_user_select)

        all_subject = []

        if action == "finish":
            if len(local_user_select) < 3:
                await bot.send_message(chat_id=callback.from_user.id,
                                       text="Ти обрав недостатню кількість предметів❗")
                return
            else:
                await callback.message.edit_text(text=f"<b>Ти вибрав:</b> {user_value} предмета",
                                                 parse_mode=ParseMode.HTML)

                for value in local_user_select:
                    selected_subject = database.get_selected_subject(value['name'])
                    all_subject += selected_subject

                if not all_subject:
                    await callback.message.answer("Nothing(")
                    return await callback.answer()

                message_text = f"📚 <b>Перелік вибіркових дисциплін:</b>\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️️\n"
                for row in all_subject:
                    message_text += f"    ▫️ {row[0]}\n"

                await bot.send_message(chat_id=callback.from_user.id,
                                       text=message_text,
                                       reply_markup=kb.get_info(),
                                       parse_mode=ParseMode.HTML)
                sticker = "CAACAgIAAxkBAAEL7oZmH8LmDUUNYc51RyQ1P5k8Bud0ywACjwADFkJrCr24snHVnwbiNAQ"
                await callback.message.answer_sticker(sticker)
                await callback.message.answer(text=f"{callback.from_user.full_name}, твій розклад готовий✅\n\n"
                                                   f"Вибери день:",
                                              reply_markup=kb.schedule_keyboard(),
                                              parse_mode=ParseMode.HTML)
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


# --------------------------For other options---------------------------
@dp.message(F.text.lower() == "коли заліки?")
async def when_session(message: Message):
    await message.reply("🔹З 15 по 31 травня(для всіх груп):\n "
                        "  1️⃣ ЗУВД \n"
                        "  🎓 Комісарчук В.В.\n"
                        "  📅 16.05.24\n\n"
                        "  2️⃣ Моделювання систем*\n"
                        "  🎓 Антонюк С.В.\n"
                        "  📅 17.05.24\n\n"
                        "  3️⃣ Протоколи та сервіси Інтернет\n"
                        "  🎓 Антонюк С.В.\n"
                        "  📅 21.05.24\n\n"
                        "  4️⃣ Теорія інформації та кодування\n"
                        "  🎓 Воробець Г.І.\n"
                        "  📅 21.05.24\n\n"
                        "  5️⃣ Програмування мобільних додатків\n"
                        "  🎓 Коцур М.П.\n"
                        "  📅 23.05.24\n\n"
                        "  6️⃣ Програмування мовою Ruby\n"
                        "  🎓 Фратавчан В.Г.\n"
                        "  📅 24.05.24\n\n")


@dp.message(F.text.lower() == "коли сесія?")
async def when_test(message: Message):
    await message.reply("🔸З 1 по 21 червня")


@dp.message(F.text.lower() == "скинути налаштування❌")
async def reset_settings(message: Message):
    global get_id
    get_id = None
    get_id = message.from_user.id

    user_select[message.from_user.id] = []
    user_data[message.from_user.id] = 0

    random_sticker = random.choice(sticker_list)

    await message.answer_sticker(sticker=random_sticker)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Привіт знову, {message.from_user.full_name}🧑🏻‍🎓! Вибери свою підгрупу:",
                           reply_markup=kb.start())


# -----------------------For the schedule------------------------
@dp.callback_query(F.data.startswith('weekday_'))
async def process_weekday_callback(callback: CallbackQuery):
    with ((suppress(TelegramBadRequest))):
        await callback.answer()

        # for user
        local_user_group = user_group.get(callback.from_user.id, {})
        local_user_select = user_select.get(callback.from_user.id, [])

        info_group = ""
        info_select = []

        for i in local_user_group.values():
            info_group = i

        message_schedule = f"📋<b>Розклад для групи:</b> {info_group}\n"

        for i in local_user_select:
            for j in i.values():
                info_select.append(j)

        info_select_tuple = tuple(info_select)

        print(user_group)
        print(user_select)
        print(info_group)
        print(info_select_tuple)

        weekday_map = {
            'monday': 'Понеділок',
            'tuesday': 'Вівторок',
            'wednesday': 'Середа',
            'thursday': 'Четвер',
            'friday': "П''ятниця"
        }

        weekday_buttons = {
            'monday': "Пн✅",
            'tuesday': "Вт✅",
            'wednesday': "Ср✅",
            'thursday': "Чт✅",
            'friday': "Пт✅"
        }

        weekday = callback.data.split('_')[1]
        name_day = weekday_map[weekday]
        button = weekday_buttons[weekday]

        calendar.setfirstweekday(calendar.SUNDAY)
        current_date = datetime.now()
        week_number = current_date.isocalendar()[1]

        if current_date.weekday() == 6:
            week_number -= 1

        if week_number % 2 == 0:
            message_schedule += "🔸<b>Тиждень:</b> ІІ\n\n"
            schedule = database.get_all_subject_second_week(info_group, info_select_tuple, name_day)
        else:
            message_schedule += "🔸<b>Тиждень:</b> І\n\n"
            schedule = database.get_all_subject_first_week(info_group, info_select_tuple, name_day)

        # for weekday
        previous_weekday = ""

        emoji_map = {
            '1': '1️⃣',
            '2': '2️⃣',
            '3': '3️⃣',
            '4': '4️⃣',
            '5': '5️⃣',
            '6': '6️⃣'
        }

        if not schedule:
            message_schedule += "Вітаю! Сьогодні в тебе вихідний, для тебе пар нема🥳"
        else:
            for values in schedule:
                weekday = values[0]
                if weekday != previous_weekday:
                    message_schedule += f"📆<b>{weekday}:</b>\n➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    previous_weekday = weekday

                lesson_number = ''.join([emoji_map.get(char, char) for char in str(values[1])])
                message_schedule += f"<b>{lesson_number} {values[2]}</b>\n"
                message_schedule += f"     🎓 {values[3]} {values[4]}\n"
                message_schedule += f"     ◻️ {values[5]}\n"
                message_schedule += f"     📍 {values[6]} ауд.\n"
                message_schedule += f"     🕓 {values[7]}-{values[8]}\n"
                message_schedule += f"     📝 {values[9]}\n\n"

        await bot.edit_message_text(chat_id=callback.message.chat.id,
                                    message_id=callback.message.message_id,
                                    text=message_schedule,
                                    reply_markup=kb.schedule_keyboard(new_button_text=button),
                                    parse_mode=ParseMode.HTML)

        await asyncio.sleep(1)


# --------------------------For links-----------------------------
@dp.callback_query(F.data == "links")
async def callback_button_links(callback: CallbackQuery):
    with suppress(TelegramBadRequest):
        await callback.answer()

        user_states[callback.from_user.id] = "schedule"
        await bot.edit_message_text(chat_id=callback.message.chat.id,
                                    message_id=callback.message.message_id,
                                    text="Вибери потрібний навчальний ресурс нижче⬇\n")
        await callback.message.edit_reply_markup(reply_markup=kb.links_keyboard())


@dp.callback_query(F.data.startswith("link_"))
async def callback_button_get_link(callback: CallbackQuery):
    with suppress(TelegramBadRequest):
        await callback.answer()

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

        name_link = callback.data.split("_")[1]

        links = database.get_links(info_group, info_select_tuple, name_link)

        message_links = ""

        if not links:
            message_links += "Упс, для тебе поки нічого нема("
        else:
            for values in links:
                message_links += f"📚 <b>{values[0]}:</b>\n➖➖➖➖➖➖➖➖➖➖➖➖\n"
                message_links += f"   🔗 {values[1]}\n"
                if values[2] is None:
                    password = "Без пароля"
                    message_links += f"   🔓 {password}\n\n"
                else:
                    password = values[2]
                    message_links += f"   🔐 \"{password}\"\n\n"

        await bot.edit_message_text(chat_id=callback.message.chat.id,
                                    message_id=callback.message.message_id,
                                    text=message_links,
                                    reply_markup=kb.links_keyboard(),
                                    parse_mode=ParseMode.HTML)


@dp.callback_query(F.data == "back")
async def callback_button_back(callback: CallbackQuery):
    with suppress(TelegramBadRequest):
        await callback.answer()

        state = user_states.get(callback.from_user.id, "schedule")
        if state == "schedule":
            await bot.edit_message_text(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id,
                                        text="Виберіть день тижня:")
            await callback.message.edit_reply_markup(reply_markup=kb.schedule_keyboard())
        elif state == "links":
            await bot.edit_message_text(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id,
                                        text="Виберіть потрібний вам ресурс нижче⬇")
            await callback.message.edit_reply_markup(reply_markup=kb.links_keyboard())


# -----------------------------For the notification------------------------------
async def send_notification():
    global get_id
    current_datetime = datetime.now()

    if get_id is not None:
        if current_datetime.weekday() == 6 and current_datetime.hour >= 10 and current_datetime.minute == 0:
            await bot.send_message(chat_id=get_id,
                                   text=f"Привіт! Завтра почнеться новий тиждень. Тицьни на день в розкладі, "
                                        f"який тебе цікавить)")
    else:
        print("I don't know anyone(")


async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_notification, "cron", day_of_week="sun", hour=10, minute=0)
    scheduler.start()

    await on_startup(None)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())