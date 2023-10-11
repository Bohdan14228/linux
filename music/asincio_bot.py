from aiogram import Bot, Dispatcher, executor, types
from keyboard import *
from sql_asyncio import *


API_TOKEN = '6124666764:AAEsHWHqaUfFKmokV9BhELYx6Q5rEpy_Rco'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
audio_name_id = []


async def not_playlist(message, text='Ви ще не створили жодного плейлисту'):
    await message.delete()
    await message.answer(text, reply_markup=await main_menu())


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.from_user.last_name is None:
        name = f"{message.from_user.first_name}"
    else:
        name = f"{message.from_user.first_name} {message.from_user.last_name}"
    mes = f'Привіт, {name}'
    await message.answer(text=mes, reply_markup=await main_menu())
    await add_user(message.from_user.id)
    await message.delete()


@dp.message_handler(content_types=['audio'])
async def audio_handler(message: types.Message):
    global audio_name_id
    if message.audio.performer is None and message.audio.title is None:
        audio_name_id.append(message.audio.file_name.replace("'", ''))
    else:
        audio_name_id.append(f"{message.audio.performer} {message.audio.title}".replace("'", ''))
    audio_name_id.append(message.audio.file_id)
    audio_name_id.append(message.chat.id)
    if await check_playlist(message.chat.id):
        await message.delete()
        await message.answer(f'Виберіть плейлист для добавлення пісні: <b>{audio_name_id[0]}</b>',
                             parse_mode='HTML',
                             reply_markup=await inline('supplement', message.chat.id))
    else:
        await message.answer('Ви ще не створили жодного плейлиста\nСтворіть плейлист і відправте трек наново')


@dp.message_handler()
async def mess(message: types.Message):
    if message.text == 'Створити плейлист':
        await message.answer('Напишіть назву плейлисту')

    elif message.text == 'Видалити' or message.text == 'Ні':
        await message.delete()
        await message.answer('Видалити', reply_markup=await delete())

    elif message.text == 'Назад':
        await message.delete()
        await message.answer('Назад', reply_markup=await main_menu())

    elif message.text == 'Показати плейлисти':
        if await check_playlist(message.chat.id):
            for i in await check_playlist(message.chat.id):
                await message.answer(i)
        else:
            await not_playlist(message)

    elif message.text == 'Почати прослуховування':
        if await check_playlist(message.chat.id):
            await message.delete()
            await message.answer(f'Виберіть плейлист',
                                 reply_markup=await inline('listen_playlist', message.chat.id))
        else:
            await not_playlist(message)

    elif message.text == 'Видалити' or message.text == 'Ні':
        await message.edit_text('Видалити', reply_markup=await del_menu())

    elif message.text == 'Видалити плейлист з усім вмістом':
        if await check_playlist(message.chat.id):
            # print(check_playlist(message.chat.id))
            await message.delete()
            await message.answer(f'Виберіть плейлист для видалення',
                                 reply_markup=await inline('delete_playlist', message.chat.id))
        else:
            await not_playlist(message)

    elif message.text == 'Видалити конкретний трек':
        if await check_playlist(message.chat.id):
            await message.delete()
            await message.answer('Виберіть плейлист для видалення треку',
                                 reply_markup=await inline('delete_trak', message.chat.id))

    else:
        await message.delete()
        await message.answer(f'Створити плейлист з назвою:\n <b>{message.text}</b>',
                             parse_mode='HTML',
                             reply_markup=await yes_or_not(message.text))


@dp.callback_query_handler()
async def ikb_close(callback: types.CallbackQuery):
    global audio_name_id
    if callback.data.startswith('supplement'):
        name_playlist = callback.data.replace('supplement', '')
        await add_track(name_playlist, audio_name_id[0], audio_name_id[1], audio_name_id[2])
        await callback.message.delete()
        await callback.message.answer(f'Додано <b>{audio_name_id[0]}</b>\nдо <b>{name_playlist}</b>',
                                      reply_markup=await main_menu(), parse_mode='HTML')
        audio_name_id = []

    elif callback.data == 'close':
        await callback.message.delete()

    elif callback.data == 'cancellation':
        await callback.message.delete()
        audio_name_id = []

    elif callback.data.startswith('yes'):
        name_playlist = callback.data.replace('yes', '')
        await add_playlist(callback.message.chat.id, name_playlist)
        await callback.answer(f'Створено {name_playlist}')
        await callback.message.delete()

    elif callback.data.startswith('listen_playlist'):
        name_playlist = callback.data.replace('listen_playlist', '')
        await callback.message.delete()
        playlist = await listen_playlist(callback.message.chat.id, name_playlist)
        if playlist:
            for i in playlist:
                await bot.send_audio(callback.message.chat.id, i)
        else:
            await callback.message.answer('В цьому плейлисті немає треків')

    elif callback.data.startswith('delete_playlist'):
        name_playlist = callback.data.replace('delete_playlist', '')
        await callback.message.edit_text(await delete_playlist_or_track(
            callback.message.chat.id, name_playlist, delete_playlist='yes'), parse_mode='HTML')

    elif callback.data.startswith('delete_trak'):
        name_track = callback.data.replace('delete_trak', '')
        await callback.message.delete()
        if await delete_track(callback.message.chat.id, name_track):
            await callback.message.answer('Виберіть трек для видалення',
                                          reply_markup=await delete_track(callback.message.chat.id, name_track))
        else:
            await callback.message.answer(f'В цьому плейлисті немає треків')

    elif callback.data.startswith('del_track'):
        id_track = callback.data.replace('del_track', '')
        await callback.message.delete()
        await callback.message.answer(await del_track(id_track), reply_markup=await del_menu(), parse_mode='HTML')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)