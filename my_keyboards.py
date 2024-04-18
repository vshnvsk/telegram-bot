from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


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


def get_keyboard_select(has_selection: bool) -> InlineKeyboardMarkup:
    # setting up the selection button
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Програмування мовою Ruby", callback_data="select_ruby")],
        [InlineKeyboardButton(text="Програмування мобільних додатків", callback_data="select_mobileapps")],
        [InlineKeyboardButton(text="Протоколи та сервіси Інтернет", callback_data="select_internet")],
        [InlineKeyboardButton(text="Теорія інформації та кодування", callback_data="select_infocode")],
        [InlineKeyboardButton(text="UX/UI дизайн та Web Usability", callback_data="select_webdesign")],
        [InlineKeyboardButton(text="Практика особистої та ділової комунікації іноземною мовою",
                              callback_data="select_english")],
        [InlineKeyboardButton(text="Скасувати❌", callback_data="select_reset")],
        [InlineKeyboardButton(text="Готово✅", callback_data="select_finish")]
    ])

    if has_selection:
        buttons.insert(-1, [InlineKeyboardButton(text="Скасувати❌", callback_data="select_reset")])

    return buttons


def get_info() -> ReplyKeyboardMarkup:
    buttons = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Коли заліки?")],
        [KeyboardButton(text="Коли сесія?")],
        [KeyboardButton(text="Скинути налаштування❌")]
    ], resize_keyboard=True, input_field_placeholder="Виберіть")

    return buttons


def schedule_keyboard(new_button_text=None) -> InlineKeyboardMarkup:
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Пн", callback_data="weekday_monday"),
            InlineKeyboardButton(text="Вт", callback_data="weekday_tuesday"),
            InlineKeyboardButton(text="Ср", callback_data="weekday_wednesday"),
            InlineKeyboardButton(text="Чт", callback_data="weekday_thursday"),
            InlineKeyboardButton(text="Пт", callback_data="weekday_friday")
        ],
        [InlineKeyboardButton(text="📎 Посилання", callback_data="links")]
    ])

    if new_button_text:
        day_to_callback = {
            'Пн✅': 'weekday_monday',
            'Вт✅': 'weekday_tuesday',
            'Ср✅': 'weekday_wednesday',
            'Чт✅': 'weekday_thursday',
            'Пт✅': 'weekday_friday'
        }
        for button in buttons.inline_keyboard[0]:
            if button.callback_data == day_to_callback.get(new_button_text):
                button.text = new_button_text
                break

    return buttons


def links_keyboard() -> InlineKeyboardMarkup:
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Meets", callback_data="link_meet"),
            InlineKeyboardButton(text="Classroom", callback_data="link_classroom"),
            InlineKeyboardButton(text="Moodle", callback_data="link_moodle")
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

    return buttons