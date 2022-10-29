import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect('petition.db')
    cur = base.cursor()
    if base:
        print('Datebase connected OK')
    base.execute(
        'CREATE TABLE IF NOT EXISTS users(user_id TEXT PRIMARY KEY, username TEXT, name TEXT, phone TEXT, is_blocked '
        'TEXT)')

    base.commit()


async def get_users():
    result = []
    for item in cur.execute('SELECT user_id FROM users').fetchall():
        result.append(int(item[0]))
    return result


async def sql_add_user(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def get_user_by_id(user_id):
    result = cur.execute('SELECT username, name, phone FROM users WHERE user_id = (?)', (user_id,)).fetchone()
    return result


async def get_phone(user_id):
    result = cur.execute('SELECT phone FROM users WHERE user_id = (?)', (user_id,)).fetchone()[0]
    return result


async def get_name(user_id):
    result = cur.execute('SELECT name FROM users WHERE user_id = (?)', (user_id,)).fetchone()[0]
    return result


async def change_phone(user_id, new_phone):
    cur.execute('UPDATE users SET phone = ? WHERE user_id = ?', (new_phone, user_id))
    base.commit()


async def change_name(user_id, new_name):
    cur.execute('UPDATE users SET name = ? WHERE user_id = ?', (new_name, user_id))
    base.commit()


async def find_user(param):
    result_list = []
    by_id = cur.execute('SELECT * FROM users WHERE user_id = (?)', (param.strip(),)).fetchall()
    by_username = cur.execute('SELECT * FROM users WHERE username = (?)', (param.strip(),)).fetchall()
    by_name = cur.execute('SELECT * FROM users WHERE name = (?)', (param.strip(),)).fetchall()
    by_phone = cur.execute('SELECT * FROM users WHERE phone = (?)', (param.strip(),)).fetchall()
    result_list.extend(by_phone)
    result_list.extend(by_name)
    result_list.extend(by_username)
    result_list.extend(by_id)
    return result_list


async def block_user(user_id, is_blocking):
    cur.execute('UPDATE users SET is_blocked = ? WHERE user_id = ?', (is_blocking, user_id))
    base.commit()


async def blocked_users():
    result = cur.execute('SELECT user_id, name FROM users WHERE is_blocked = "True"').fetchall()
    return result


async def filter_block_filter():
    result = []
    for item in cur.execute('SELECT user_id FROM users WHERE is_blocked = "True"').fetchall():
        result.append(int(item[0]))
    return result

# sql_start()
# asyncio.run(get_username())
