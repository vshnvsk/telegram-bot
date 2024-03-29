from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def start() -> ReplyKeyboardMarkup:
    kb = [
        [
            KeyboardButton(text="341А"),
            KeyboardButton(text="341Б"),
            KeyboardButton(text="341СК")
        ],
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Вибери підгрупу"
    )

    return keyboard