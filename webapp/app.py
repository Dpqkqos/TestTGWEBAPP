import os
from aiohttp import web
import aiosqlite
from datetime import datetime

# Конфигурация
DB_PATH = os.getenv("DB_PATH", "user_states.db")
PORT = int(os.getenv("PORT", 8080))

async def init_db(app):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS records
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           chat_id INTEGER NOT NULL,
                           state TEXT NOT NULL,
                           date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        await db.commit()

async def get_records(chat_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT date, state FROM records WHERE chat_id = ? ORDER BY date DESC",
            (chat_id,)
        )
        return await cursor.fetchall()

async def save_record(chat_id, state):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO records (chat_id, state) VALUES (?, ?)",
            (chat_id, state)
        )
        await db.commit()

# Обработчики
async def handle_table(request):
    chat_id = request.query.get("chat_id")
    if not chat_id:
        return web.Response(text="chat_id required", status=400)
    
    try:
        records = await get_records(int(chat_id))
    except ValueError:
        return web.Response(text="Invalid chat_id", status=400)

    rows = "".join(
        f'<tr><td>{datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M")}</td>'
        f'<td>{r[1]}</td></tr>'
        for r in records
    )

    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Журнал состояний</title>
        <link rel="stylesheet" href="/static/style.css">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <div class="container">
            <h1>📆 История состояний</h1>
            <table>
                <thead>
                    <tr><th>Дата</th><th>Состояние</th></tr>
                </thead>
                <tbody>
                    {rows or '<tr><td colspan="2">😕 Нет записей</td></tr>'}
                </tbody>
            </table>
        </div>
    </body>
    </html>"""
    
    return web.Response(text=html, content_type="text/html")

async def handle_api(request):
    data = await request.post()
    try:
        await save_record(int(data["chat_id"]), data["state"])
        return web.Response(text="OK")
    except (KeyError, ValueError):
        return web.Response(text="Invalid data", status=400)

# Инициализация приложения
app = web.Application()
app.on_startup.append(init_db)
app.router.add_get("/", handle_table)
app.router.add_post("/api/user-state/", handle_api)
app.router.add_static("/static/", path="static")

if __name__ == "__main__":
    web.run_app(app, port=PORT)