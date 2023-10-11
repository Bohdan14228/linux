from aiogram import Bot, Dispatcher, executor, types
from keyboard import *
from admin_base import admin_base
from sqlite import *
import aiosqlite
import aiogram
import uuid
from thagotovki import *
import os

API_TOKEN = '5993455599:AAF5T1T_U0Mgglb7aCMJLXQfnXRaW8Zt-_U'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

text_record = ''


async def on_startup(_):
    print('BOT go')


async def examination_in_base(user_id):
    return user_id in admin_base


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.from_user.last_name is None:
        name = f"{message.from_user.first_name}"
    else:
        name = f"{message.from_user.first_name} {message.from_user.last_name}"
    mess = f'Привіт, {name}'
    await message.answer(text=mess, reply_markup=await func_kb(message.from_user.id))
    await add_user(message.from_user.id, name, message.from_user.username)
    await message.delete()


@dp.message_handler()
async def send_user_id(message: types.Message):
    global text_record
    if message.text == 'Твій user_id':
        await message.reply(message.from_user.id)

    elif message.text == 'Адмін-панель':
        if await examination_in_base(message.from_user.id):
            await message.answer(text='Адмін-панель', reply_markup=await func_admin_ikb())
        else:
            await message.answer('У вас недостатньо прав', reply_markup=await func_kb(message.from_user.id))
        await message.delete()

    elif message.text == 'Інструкція':
        await message.delete()
        await message.answer('Виберіть інструкцію для якої платформи', reply_markup=await ikb_for_platforms('show'))
    # добавление ссылок на статьи
    elif message.entities and message.entities[0].type == 'url':
        await message.delete()
        text_record = message.text
        if await examination_in_base(message.from_user.id):
            await message.answer('Посилання буде додано до', reply_markup=await ikb_for_platforms('add_url'))
        else:
            await message.delete()
            await message.answer('У вас недостатньо прав щоб додавати інструкції',
                                 reply_markup=await func_kb(message.from_user.id))

    else:
        await message.delete()
        if await examination_in_base(message.from_user.id):
            await message.answer('Заголовок інструкції буде створено для', reply_markup=await add_header(message.text))
        else:
            await message.delete()
            await message.answer('У вас недостатньо прав щоб додавати інструкції',
                                 reply_markup=await func_kb(message.from_user.id))


@dp.callback_query_handler()
async def ikb_close(callback: types.CallbackQuery):
    global text_record
    # закрытие
    if callback.data == 'close':
        await callback.message.delete()
    # добавление заголовка в одну из платформ
    elif callback.data.startswith('Кіпер') or callback.data.startswith('1С'):
        if callback.data.startswith('Кіпер'):
            text1 = callback.data.replace('Кіпер', '')
        else:
            text1 = callback.data.replace('1С', '')
        await callback.message.delete()
        if await add_instruction(text1, plt=callback.data.replace(text1, '')):
            await callback.message.answer(f'Додано новий заголовок:\n<b>{text1}</b>', parse_mode='HTML',
                                          reply_markup=await func_kb(callback.from_user.id))
        else:
            await callback.message.answer('Такий заголовок вже існує')
    # добавление ссылки в одну из платформ
    elif callback.data == 'add_urlКіпер' or callback.data == 'add_url1С':
        if 'Кіпер' in callback.data:
            text1 = callback.data.replace('add_url', '')
        else:
            text1 = callback.data.replace('add_url', '')
        await callback.message.delete()
        if await examination_in_base(callback.from_user.id):
            record_ikb = await add_records_ikb(text1)
            if not record_ikb:
                await callback.message.answer('Всі заголовки зайняти, створіть новий')
            else:
                await callback.message.answer(f"Виберіть заголовок для цього посилання",
                                              reply_markup=record_ikb)
        else:
            await callback.message.answer('У вас недостатньо прав щоб додавати інструкції',
                                          reply_markup=await func_kb(callback.from_user.id))

    elif callback.data == 'showКіпер' or callback.data == 'show1С':
        if 'Кіпер' in callback.data:
            text1 = callback.data.replace('show', '')
        else:
            text1 = callback.data.replace('show', '')
        await callback.message.delete()
        try:
            await callback.message.answer('Інструкції', reply_markup=await ikb_instructions(text1))
        except aiogram.utils.exceptions.BadRequest:
            await callback.message.answer('Ви додали інструкцію не як посилання, а як текст')

    elif callback.data.startswith('add_records'):
        await add_records(callback.data.replace('add_records', ''), text_record)
        await callback.answer('Додано новий текст інструкції')
        await callback.message.delete()

    elif callback.data.startswith('show_instruction'):
        text = callback.data.replace('show_instruction', '')
        await callback.message.answer(await show_records(text))

    elif callback.data.startswith('del') or callback.data == 'back':
        await callback.message.delete()
        await callback.message.answer('Де хочете видалити', reply_markup=await ikb_for_platforms('instr_del'))
        # await callback.message.edit_text('Виберіть інструкцію яку хочете видалити',
        #                                  reply_markup=await del_instruction_step_1())

    elif callback.data.startswith('instr_del'):
        plt = callback.data.replace('instr_del', '')
        await callback.message.edit_text('Виберіть інструкцію яку хочете видалити',
                                         reply_markup=await del_instruction_step_1(plt))

    elif callback.data.startswith('instruction_del_step_1'):
        text = callback.data.replace('instruction_del_step_1', '')
        if text.startswith('del'):
            await callback.message.delete()
            text = text.replace('del', '')
            await callback.message.answer('Виберіть що саме хочете видалити',
                                          reply_markup=await del_instruction_step_2(text))
        else:
            await del_problems(text)
            await callback.answer('Видалено')
            await callback.message.delete()

    elif callback.data.startswith('instruction_del_1'):
        await callback.answer('Видалено')
        text = callback.data.replace('instruction_del_1', '')
        await del_records_problems(text, 1)
        await callback.message.delete()

    elif callback.data.startswith('instruction_del_2'):
        await callback.answer('Видалено')
        text = callback.data.replace('instruction_del_2', '')
        await del_records_problems(text, 2)
        await callback.message.delete()


@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery) -> None:
    text = inline_query.query or None
    inline_set = []
    for i in slovar:
        item1 = InlineQueryResultArticle(
            input_message_content=InputTextMessageContent(message_text=f"{slovar[i]}", parse_mode='markdown'),
            id=str(uuid.uuid4()),
            title=f"{i}",
        )
        inline_set.append(item1)

    inline_set.append(
        InlineQueryResultArticle(
            input_message_content=InputTextMessageContent(
                message_text=f"*Шестерёнка – админ – настройки - ФР* нажмите на *Порт*,\
                                выберете tcp и пишите *{text}*, сохраните дискета слева\
                                внизу и проверьте связь *шестерёнка – касса – проверка\
                                связи ФР* и фото", parse_mode='markdown'),
            id=str(uuid.uuid4()),
            title=f"{'IP порт на ФР'}",
            description='Впишите IP'
        )
    )

    inline_set.extend(drugoe)

    await bot.answer_inline_query(inline_query_id=inline_query.id,
                                  results=inline_set,
                                  cache_time=1)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
