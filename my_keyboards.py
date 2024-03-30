from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start() -> InlineKeyboardMarkup:
    # setting up the start button
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="341А", callback_data="group_341A"),
            InlineKeyboardButton(text="341Б", callback_data="group_341Б"),
            InlineKeyboardButton(text="341СК", callback_data="group_341CK")
        ]
    ])

    return buttons


def get_keyboard_select() -> InlineKeyboardMarkup:
    # setting up the selection button
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Програмування мовою Ruby", callback_data="select_ruby")],
        [InlineKeyboardButton(text="Програмування мобільних додатків", callback_data="select_mobileapps")],
        [InlineKeyboardButton(text="Протоколи та сервіси Інтернет", callback_data="select_internet")],
        [InlineKeyboardButton(text="Теорія інформації та кодування", callback_data="select_infocode")],
        [InlineKeyboardButton(text="UX/UI дизайн та Web Usability", callback_data="select_webdesign")],
        [InlineKeyboardButton(text="Практика особистої та ділової комунікації іноземною мовою", callback_data="select_english")],
        [InlineKeyboardButton(text="Готово✅", callback_data="select_finish")]
    ])

    return buttons