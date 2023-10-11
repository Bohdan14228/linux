import aiosqlite
import asyncio


async def add_user(user) -> None:
    async with aiosqlite.connect('playlists.db') as db:
        await db.execute(f"INSERT INTO users(user) VALUES (?)", (user,))
        await db.commit()


async def check_playlist(chat_id):
    async with aiosqlite.connect('playlists.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT name_genre FROM playlist "
                             f"WHERE user_id LIKE (SELECT id FROM users WHERE user LIKE ?)", (chat_id,))
        return [i[0] for i in await cursor.fetchall()]
# print(asyncio.get_event_loop().run_until_complete(check_playlist(428392590)))


async def add_playlist(user_id, name_genre) -> None:
    async with aiosqlite.connect('playlists.db') as db:
        await db.execute(
            "INSERT INTO playlist (user_id, name_genre) VALUES ((SELECT id FROM users WHERE user = ?), ?)",
            (user_id, name_genre))
        await db.commit()


async def add_track(name_playlist, name_track, id_track, user_id) -> None:
    async with aiosqlite.connect('playlists.db') as db:
        await db.execute(
            "INSERT INTO tracks (playlist_id, name_track, id_track) "
            "VALUES ((SELECT id FROM playlist WHERE user_id = (SELECT id FROM users WHERE user = ?)"
            " AND name_genre = ?), ?, ?)",
            (user_id, name_playlist, name_track, id_track))
        await db.commit()


async def listen_playlist(chat_id, name_playlist):
    async with aiosqlite.connect('playlists.db') as db:
        cursor = await db.cursor()
        await cursor.execute(
            "SELECT id_track FROM tracks WHERE playlist_id LIKE "
            "(SELECT id FROM playlist WHERE name_genre = ? AND user_id ="
            "(SELECT id FROM users WHERE user = ?))", (name_playlist, chat_id))
        return [i[0] for i in await cursor.fetchall()]
        # return await cursor.fetchall()


async def delete_playlist_or_track(chat_id, name_playlist, delete_playlist=''):
    async with aiosqlite.connect('playlists.db') as db:
        await db.execute("DELETE FROM tracks WHERE playlist_id = "
                         "(SELECT id FROM playlist WHERE name_genre = ? AND user_id = "
                         "(SELECT id FROM users WHERE user = ?))", (name_playlist, chat_id))
        if delete_playlist:
            await db.execute(
                "DELETE FROM playlist WHERE name_genre = ? AND user_id = "
                "(SELECT id FROM users WHERE user = ?)", (name_playlist, chat_id))
        await db.commit()
        if delete_playlist:
            return f'Ви видалили плейлист: <u><b>{name_playlist}</b></u>'
        else:
            return ''


async def trak_in_playlist(chat_id, name_playlist):
    async with aiosqlite.connect('playlists.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT id, name_track FROM tracks WHERE playlist_id ="
                             "(SELECT id FROM playlist WHERE name_genre = ? AND user_id = "
                             "(SELECT id FROM users WHERE user = ?))", (name_playlist, chat_id))
        return await cursor.fetchall()


async def del_track(track_id):
    async with aiosqlite.connect('playlists.db') as db:
        cursor1 = await db.cursor()
        playlist = await cursor1.execute('SELECT name_genre FROM playlist WHERE id = '
                                         '(SELECT playlist_id from tracks WHERE id = ?)',
                                         (track_id,))
        cursor2 = await db.cursor()
        track = await cursor2.execute('SELECT name_track FROM tracks WHERE id = ?', (track_id,))
        await db.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
        await db.commit()
        return f'Видалено\n<u>{(await track.fetchall())[0][0]}</u>\nз плейлисту\n' \
               f'<u>{(await playlist.fetchall())[0][0]}</u>'
        # return (await track.fetchall())[0][0], (await playlist.fetchall())[0][0]

# print(asyncio.get_event_loop().run_until_complete(del_track(17)))


# async def select(user, name_genre):
#     async with aiosqlite.connect('playlists.db') as db:
#         cursor = await db.cursor()
#         await cursor.execute("SELECT id FROM playlist WHERE user_id = (SELECT id FROM users WHERE user = ?) "
#                              "AND name_genre = ?", (user, name_genre))
#         return await cursor.fetchall()
#
# print(asyncio.get_event_loop().run_until_complete(trak_in_playlist(428392590, 'Фонк')))
# print(asyncio.get_event_loop().run_until_complete(select()))
