import os
from dotenv import load_dotenv
import datetime
import aiosqlite

load_dotenv()

TOKEN = os.getenv('TOKEN')
DB_FILE = 'users.db'
    
async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                passed INTEGER DEFAULT 0,
                attempts INTEGER DEFAULT 0,
                last_captcha INTEGER,
                captcha_time TIMESTAMP
            )
        ''')
        await db.commit()

async def user_passed(user_id: int) -> bool:
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT passed FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return bool(row and row[0] == 1)

async def save_captcha(user_id: int, correct: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('''
            INSERT INTO users (user_id, last_captcha, captcha_time, passed)
            VALUES (?, ?, ?, 0)
            ON CONFLICT(user_id) DO UPDATE SET
                last_captcha = excluded.last_captcha,
                captcha_time = excluded.captcha_time,
                passed = 0
        ''', (user_id, correct, datetime.now()))
        await db.commit()

async def check_answer(user_id: int, answer: int) -> bool:
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT last_captcha FROM users WHERE user_id = ? AND passed = 0", (user_id,)) as cur:
            row = await cur.fetchone()
            if row and row[0] == answer:
                await db.execute("UPDATE users SET passed = 1 WHERE user_id = ?", (user_id,))
                await db.commit()
                return True
    return False