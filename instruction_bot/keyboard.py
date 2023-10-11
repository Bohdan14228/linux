from aiogram.types import *
from sqlite import *
from admin_base import *


# async def examination_in_base(user_id):
#     return user_id in admin_base


async def func_kb(user_id):
    kb1 = ReplyKeyboardMarkup(resize_keyboard=True)
    if user_id not in admin_base:
        kb1.add(KeyboardButton('Твій user_id'),
                KeyboardButton('Інструкція'))
    else:
        kb1.add(KeyboardButton('Твій user_id'),
                KeyboardButton('Інструкція')).add(KeyboardButton('Адмін-панель'))
    return kb1


async def func_admin_ikb():
    admin_ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Видалити 'Інструкцію'", callback_data='del')],
        [InlineKeyboardButton('Закрити', callback_data='close')]
    ]
    )
    return admin_ikb


async def func_add_text_ikb():
    add_text_ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Додати як заголовок 'Інструкції'", callback_data='add_header')],
        [InlineKeyboardButton("Додати як текст 'Інструкції'", callback_data='add_text')],
        [InlineKeyboardButton("Відмінити", callback_data='close')]
    ]
    )
    return add_text_ikb


async def ikb_instructions(plt):
    ikb = InlineKeyboardMarkup(row_width=1)
    for i in await for_ikb_instructions('show', plt):
        ikb.add(InlineKeyboardButton(text=f"{i[1]}", url=f"{await show_record(i[0], 'show')}"))
    ikb.add(InlineKeyboardButton('Закрити', callback_data='close'))
    return ikb


# print(asyncio.get_event_loop().run_until_complete(ikb_instructions('1С')))


async def add_records_ikb(platform):
    if not await for_add_records_ikb(platform):
        return None
    ikb = InlineKeyboardMarkup(row_width=1)
    for i in await for_add_records_ikb(platform):
        ikb.add(InlineKeyboardButton(text=f"{i[1]}", callback_data=f"add_records{i[0]}"))
    ikb.add(InlineKeyboardButton('Закрити', callback_data='close'))
    return ikb


async def del_instruction_step_1(plt):
    ikb = InlineKeyboardMarkup(row_width=1)
    for i in await for_ikb_instructions('del', plt):
        ikb.add(InlineKeyboardButton(text=f"{i[1]}",
                                     callback_data=f"instruction_del_step_1{i[0] if not await show_record(i[0], 'id') else 'del' + str(await show_record(i[0], 'id'))}"))
    ikb.add(InlineKeyboardButton('Закрити', callback_data='close'))
    return ikb


# print(asyncio.get_event_loop().run_until_complete(del_instruction_step_1('1С')))


async def del_instruction_step_2(record_id):
    add_text_ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Видалити тільки url інструкції", callback_data=f'instruction_del_1{record_id}')],
        [InlineKeyboardButton("Видалити заголовок і url інструкції", callback_data=f'instruction_del_2{record_id}')],
        [InlineKeyboardButton("Назад", callback_data='back')],
    ]
    )
    return add_text_ikb


async def add_header(text):
    admin_ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Кіпер", callback_data=f'Кіпер{text}')],
        [InlineKeyboardButton("1С", callback_data=f'1С{text}')],
        [InlineKeyboardButton('Закрити', callback_data='close')]
    ]
    )
    return admin_ikb


async def ikb_for_platforms(callback):
    admin_ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Кіпер", callback_data=f'{callback}Кіпер')],
        [InlineKeyboardButton("1С", callback_data=f'{callback}1С')],
        [InlineKeyboardButton('Закрити', callback_data='close')]
    ]
    )
    return admin_ikb
