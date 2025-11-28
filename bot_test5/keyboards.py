#вёрстка клавиатур
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Консультация", callback_data="consultation"),
    InlineKeyboardButton(text="Мой ТГ-канал", url='https://t.me/+mX695lhKCAxhOGVi')],
    [InlineKeyboardButton(text="Акции", callback_data="action"),
    InlineKeyboardButton(text="Про продвижение", callback_data="about_promotion")],
    [InlineKeyboardButton(text="Свод предупреждений", callback_data="rules")],
]
)

consultation_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')],
    ]
)

action_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')],
    ]
)

about_promotion_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Массфолл', callback_data='subscription'),
         InlineKeyboardButton(text='Рассылка', callback_data='mailing')],
        [InlineKeyboardButton(text='Авторассылка', callback_data='auto_mailing'),
        InlineKeyboardButton(text='Комментинг в ТГ', callback_data='commenting')],
        [InlineKeyboardButton(text='ТГ-боты', callback_data='tg_bot'),
        InlineKeyboardButton(text='Прайс-лист', callback_data='price_list')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ],
)

rules_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')],
    ]
)

#Рассылка

mailing_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к ТЗ', callback_data='mailing_next_block_1')],
        [InlineKeyboardButton(text='Назад', callback_data='mailing_back_list_1')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

mailing_next_block_kb_1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='mailing_next_block_2')],
        [InlineKeyboardButton(text='Назад', callback_data='mailing_back_list_2')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

mailing_next_block_kb_2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='mailing_next_block_3')],
        [InlineKeyboardButton(text='Назад', callback_data='mailing_back_list_3')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

mailing_next_block_kb_3 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='mailing_next_block_4')],
        [InlineKeyboardButton(text='Назад', callback_data='mailing_back_list_4')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

mailing_next_block_kb_4 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='mailing_next_block_5')],
        [InlineKeyboardButton(text='Назад', callback_data='mailing_back_list_5')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

mailing_next_block_kb_5 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='mailing_next_block_6')],
        [InlineKeyboardButton(text='Назад', callback_data='mailing_back_list_6')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

mailing_next_block_kb_6 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='mailing_back_list_7')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

#Подписка

subscription_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к ТЗ', callback_data='subscription_next_block_1')],
        [InlineKeyboardButton(text='Назад', callback_data='subscription_back_list_1')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

subscription_next_block_kb_1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='subscription_next_block_2')],
        [InlineKeyboardButton(text='Назад', callback_data='subscription_back_list_2')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

subscription_next_block_kb_2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='subscription_next_block_3')],
        [InlineKeyboardButton(text='Назад', callback_data='subscription_back_list_3')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

subscription_next_block_kb_3 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='subscription_next_block_4')],
        [InlineKeyboardButton(text='Назад', callback_data='subscription_back_list_4')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

subscription_next_block_kb_4 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='subscription_next_block_5')],
        [InlineKeyboardButton(text='Назад', callback_data='subscription_back_list_5')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

subscription_next_block_kb_5 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='subscription_back_list_6')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

#Авторассылка

auto_mailing_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к ТЗ', callback_data='auto_mailing_next_block_1')],
        [InlineKeyboardButton(text='Назад', callback_data='auto_mailing_back_list_1')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

auto_mailing_next_block_kb_1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='auto_mailing_next_block_2')],
        [InlineKeyboardButton(text='Назад', callback_data='auto_mailing_back_list_2')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

auto_mailing_next_block_kb_2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='auto_mailing_next_block_3')],
        [InlineKeyboardButton(text='Назад', callback_data='auto_mailing_back_list_3')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

auto_mailing_next_block_kb_3 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='auto_mailing_next_block_4')],
        [InlineKeyboardButton(text='Назад', callback_data='auto_mailing_back_list_4')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

auto_mailing_next_block_kb_4 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='auto_mailing_next_block_5')],
        [InlineKeyboardButton(text='Назад', callback_data='auto_mailing_back_list_5')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

auto_mailing_next_block_kb_5 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='auto_mailing_next_block_6')],
        [InlineKeyboardButton(text='Назад', callback_data='auto_mailing_back_list_6')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

auto_mailing_next_block_kb_6 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='auto_mailing_next_block_7')],
        [InlineKeyboardButton(text='Назад', callback_data='auto_mailing_back_list_7')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

auto_mailing_next_block_kb_7 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='auto_mailing_next_block_8')],
        [InlineKeyboardButton(text='Назад', callback_data='auto_mailing_back_list_8')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

auto_mailing_next_block_kb_8 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='auto_mailing_next_block_9')],
        [InlineKeyboardButton(text='Назад', callback_data='auto_mailing_back_list_9')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

auto_mailing_next_block_kb_9 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='auto_mailing_back_list_10')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

#Комментинг

commenting_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к ТЗ', callback_data='commenting_next_block_1')],
        [InlineKeyboardButton(text='Назад', callback_data='commenting_back_list_1')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

commenting_next_block_kb_1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='commenting_next_block_2')],
        [InlineKeyboardButton(text='Назад', callback_data='commenting_back_list_2')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

commenting_next_block_kb_2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='commenting_next_block_3')],
        [InlineKeyboardButton(text='Назад', callback_data='commenting_back_list_3')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

commenting_next_block_kb_3 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='commenting_next_block_4')],
        [InlineKeyboardButton(text='Назад', callback_data='commenting_back_list_4')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

commenting_next_block_kb_4 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='commenting_back_list_5')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

#ТГ-боты

tg_bot_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к ТЗ', callback_data='tg_bot_next_block_1')],
        [InlineKeyboardButton(text='Назад', callback_data='tg_bot_back_list_1')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

tg_bot_next_block_kb_1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='tg_bot_next_block_2')],
        [InlineKeyboardButton(text='Назад', callback_data='tg_bot_back_list_2')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

tg_bot_next_block_kb_2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='tg_bot_next_block_3')],
        [InlineKeyboardButton(text='Назад', callback_data='tg_bot_back_list_3')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

tg_bot_next_block_kb_3 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к следующему пункту', callback_data='tg_bot_next_block_4')],
        [InlineKeyboardButton(text='Назад', callback_data='tg_bot_back_list_4')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

tg_bot_next_block_kb_4 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='tg_bot_back_list_5')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

price_list_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к оплате', url='https://t.me/ZackFosterpromotion')],
        [InlineKeyboardButton(text='Назад', callback_data='price_list_back_list_1')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

consultation_back_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)
