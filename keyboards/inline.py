from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


inline_keyboard_menu_admin_sklada = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Адреса", callback_data="Адреса")],
        [
            InlineKeyboardButton(text="Задание", callback_data="Задание"),
            InlineKeyboardButton(text="Заявка", callback_data="Заявка"),
        ],
    ]
)

inline_keyboard_menu_courier = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Оставить заявку", callback_data="Оставить_заявку"
            ),
            InlineKeyboardButton(text="Адреса", callback_data="Адреса"),
        ],
        [
            InlineKeyboardButton(
                text="Дневное Задание", callback_data="Дневное_задание"
            ),
            InlineKeyboardButton(text="Отчет", callback_data="Отчет"),
        ],
        [InlineKeyboardButton(text="День окончен", callback_data="День_окончен")],
    ]
)

inline_keyboard_menu_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Адреса", callback_data="Адреса"),
            InlineKeyboardButton(text="Задание", callback_data="Задание"),
        ],
        [
            InlineKeyboardButton(text="Заявка", callback_data="Заявка"),
            InlineKeyboardButton(text="Отчет", callback_data="Отчет"),
        ],
        [
            InlineKeyboardButton(
                text="Дневное Задание", callback_data="Дневное_задание"
            ),
            InlineKeyboardButton(
                text="Оставить заявку", callback_data="Оставить_заявку"
            ),
        ],
        [
            InlineKeyboardButton(text="День окончен", callback_data="День_окончен"),
            InlineKeyboardButton(
                text="Обновить пользователей", callback_data="Обновить_пользователей"
            ),
        ],
    ]
)


inline_keyboard_zadanie = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подтвердить", callback_data="Подтвердить_задание"
            ),
            InlineKeyboardButton(text="Добавить", callback_data="Добавить_задание"),
        ],
        [
            InlineKeyboardButton(text="Заново", callback_data="Заново_задание"),
            InlineKeyboardButton(text="Меню", callback_data="Меню"),
        ],
    ]
)

inline_keyboard_otchet = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Подтвердить", callback_data="Подтвердить_отчет"),
            InlineKeyboardButton(text="Добавить", callback_data="Добавить_отчет"),
        ],
        [
            InlineKeyboardButton(text="Заново", callback_data="Заново_отчет"),
            InlineKeyboardButton(text="Меню", callback_data="Меню"),
        ],
    ]
)

inline_keyboard_zayavka = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подтвердить", callback_data="Подтвердить_заявка"
            ),
            InlineKeyboardButton(text="Добавить", callback_data="Добавить_заявка"),
        ],
        [
            InlineKeyboardButton(text="Заново", callback_data="Заново_заявка"),
            InlineKeyboardButton(text="Меню", callback_data="Меню"),
        ],
    ]
)

inline_keyboard_denoc = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Подтвердить", callback_data="Подтвердить_день"),
            InlineKeyboardButton(text="Меню", callback_data="Меню"),
        ]
    ]
)
