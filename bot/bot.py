import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp

# Инициализация бота
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

# Клавиатура
async def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="💬 Записать состояние",
            callback_data="record_state"
        ),
        types.InlineKeyboardButton(
            text="📊 Посмотреть таблицу",
            web_app=types.WebAppInfo(url=f"{os.getenv('WEB_APP_URL')}/?chat_id={{user_id}}")
        )
    )
    return builder.as_markup()

# Обработка /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "🌞 Добро пожаловать! Выберите действие:",
        reply_markup=await main_menu()
    )

# Сохранение состояния
@dp.callback_query(lambda c: c.data == "record_state")
async def handle_record(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Опишите ваше текущее эмоциональное состояние:")
    await state.set_state("waiting_for_state")
    await callback.answer()

@dp.message(lambda message: message.text and len(message.text.strip()) > 0)
async def save_state(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{os.getenv('WEB_APP_URL')}/api/user-state/",
                data={"chat_id": message.from_user.id, "state": message.text.strip()}
            ) as response:
                if response.status == 200:
                    await message.answer("✅ Состояние сохранено!")
                else:
                    await message.answer("❌ Ошибка сохранения")
        except Exception as e:
            logging.error(f"API error: {e}")
            await message.answer("🔴 Сервис временно недоступен")
    
    await state.clear()

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp)