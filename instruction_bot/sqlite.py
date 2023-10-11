import string
import aiosqlite
import random
import asyncio


async def show_for_db(name, name_table):
    async with aiosqlite.connect('instructions.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT {name} FROM {name_table}")
        return [i[0] for i in await cursor.fetchall()]


# добавляет юзера при нажатии на команду старт
async def add_user(u_id, name, username) -> None:
    async with aiosqlite.connect('instructions.db') as db:
        cursor = await db.cursor()
        existing_users = await show_for_db(name='user_id', name_table='users')
        if str(u_id) not in existing_users:
            await cursor.execute(f"INSERT INTO users(user_id, user_name, username) VALUES (?, ?, ?)",
                                 (u_id, name, username))
            await db.commit()


# генерирует callback идентификатор
# async def generate_random_string(length):
#     return ''.join(random.choices(string.ascii_lowercase, k=length))


# async def callback_func():
#     async with aiosqlite.connect('instructions.db') as db:
#         while True:
#             a = await generate_random_string(10)
#             existing_users = await show_for_db(name='callback', name_table='problems')
#             if a not in existing_users:
#                 return a


# добавляет заголовок инструкции
# async def add_instruction(np, plt):
#     async with aiosqlite.connect('instructions.db') as db:
#         cursor = await db.cursor()
#         await cursor.execute(f'''INSERT INTO problems(name_problem, platform) VALUES (?, ?) IF {np} NOT In
# (SELECT name_problem from problems WHERE platform = {plt})''',
#                              (np, plt))
#         await db.commit()

async def add_instruction(np, plt):
    async with aiosqlite.connect('instructions.db') as db:
        cursor = await db.cursor()
        await cursor.execute(
            f'''INSERT OR IGNORE INTO problems(name_problem, platform) 
                SELECT ?, ? 
                WHERE NOT EXISTS (SELECT 1 FROM problems WHERE name_problem = ? AND platform = ?)''',
            (np, plt, np, plt)
        )
        num_rows_affected = cursor.rowcount
        if num_rows_affected == 0:
            return False
        else:
            await db.commit()
            return True


# показывает заголовки
async def show_problems():
    async with aiosqlite.connect('instructions.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT name_problem FROM problems")
        return [i[0] for i in await cursor.fetchall()]


# Для добавления текста инструкции
async def show_problemid_in_records():
    list1 = []
    for i in await show_for_db('problem_id', 'records'):
        if i in await show_for_db('id', 'problems'):
            list1.append(i)
    return list1


# для кнопок показа инструкции
async def for_ikb_instructions(comm: str, plt=''):
    async with aiosqlite.connect('instructions.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT id, name_problem FROM problems WHERE platform = ?", (plt,))
        if comm == 'show':
            return [i for i in await cursor.fetchall() if i[0] in await show_problemid_in_records()]
        else:
            return [i for i in await cursor.fetchall()]
# print(asyncio.get_event_loop().run_until_complete(for_ikb_instructions('del')))


async def show_record(problem_id, func: str):
    async with aiosqlite.connect('instructions.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT id, record FROM records WHERE problem_id = ?", (problem_id,))
        try:
            if func == 'show':
                return [i[1] for i in await cursor.fetchall()][0]
            else:
                return [i[0] for i in await cursor.fetchall()][0]
        except IndexError:
            return None
# print(asyncio.get_event_loop().run_until_complete(show_record(43, 'show')))


async def show_free_problem():
    list1 = []
    for i in await show_for_db('id', 'problems'):
        if i not in await show_for_db('problem_id', 'records'):
            list1.append(i)
    return list1


async def for_add_records_ikb(platform):
    async with aiosqlite.connect('instructions.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT id, name_problem FROM problems WHERE platform = ?", (platform,))
        return [i for i in await cursor.fetchall() if i[0] in await show_free_problem()]

# print(asyncio.get_event_loop().run_until_complete(for_add_records_ikb('1С')))


# показ инструкций, где есть записи
async def show_problem_id(callback):
    async with aiosqlite.connect('instructions.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT id FROM problems WHERE id = ?", (callback,))
        return [i[0] for i in await cursor.fetchall()][0]


# добавление записей
async def add_records(callback, record):
    async with aiosqlite.connect('instructions.db') as db:
        cursor = await db.cursor()
        await cursor.execute('''INSERT INTO records(problem_id, record) VALUES (?, ?)''',
                             (await show_problem_id(callback), record))
        await db.commit()


async def show_records(callback):
    async with aiosqlite.connect('instructions.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT record FROM records WHERE problem_id = ?", (await show_problem_id(callback),))
        return [i[0] for i in await cursor.fetchall()][0]


async def del_records_problems(record_id, step: int):
    async with aiosqlite.connect('instructions.db') as db:
        try:
            if step == 1:
                await db.execute("DELETE FROM records WHERE id = ?", (record_id,))
            else:
                await db.execute("DELETE FROM problems WHERE id IN (SELECT problem_id FROM records WHERE id = ?)",
                                 (record_id,))
                await db.execute("DELETE FROM records WHERE id = ?", (record_id,))
        except Exception as ex:
            print(ex)
        await db.commit()


async def del_problems(problem_id):
    async with aiosqlite.connect('instructions.db') as db:
        await db.execute("DELETE FROM problems WHERE id = ?", (problem_id,))
        await db.commit()

# print(asyncio.get_event_loop().run_until_complete(del_records_problems('https://telegra.ph/nmnm-06-28')))
