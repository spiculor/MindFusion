from aiogram import Router, Bot, Dispatcher
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.storage.memory import MemoryStorage
from app.auth import verify_login
from app import crud
from app.database.database import SessionLocal
from aiogram.filters import Command, CommandStart
import asyncio
from aiogram.methods import DeleteWebhook
router = Router()
bot = Bot(token="6958415246:AAFIym_1wZoJ-6WdmwTTehJ7hjSIC2AXUiU")
dp = Dispatcher(storage=MemoryStorage())


async def get_db_session():
    async with SessionLocal() as session:
        yield session


@router.message(CommandStart())
async def start_command(message: Message):
    welcome_text = (
        "Привет! Я ваш уведомляющий бот. "
        "Чтобы я мог отправлять вам уведомления, пожалуйста, войдите, используя команду /login.\n"
        "Пример: /login логин пароль\n"
        "Если у вас возникли проблемы, обратитесь к администратору."
    )
    await message.answer(welcome_text)


@router.message(Command(commands=["login"]))
async def login_command(message: Message):
    user_input = message.text.split()[1:]

    if len(user_input) != 2:

        await message.answer("Неверный формат. Введите команду в формате /login логин пароль.")
        return
    
    login, password = user_input


    async with SessionLocal() as db:
        user = await verify_login(db, login, password)

        if user:
            await crud.update_user_telegram_id(db, user.id, message.from_user.id)
            await message.answer("Вы успешно авторизовались, ваш Telegram ID сохранен!")
        else:
            await message.answer("Неверные логин или пароль.")


async def send_notification(user_id: int, message_text: str, connected_users: dict):
    async with get_db_session() as db:
        telegram_id = await crud.get_user_telegram_id(db, user_id)
        if telegram_id and user_id not in connected_users:  # Если пользователь не подключен, отправляем уведомление
            await bot.send_message(chat_id=telegram_id, text=message_text)


async def check_and_notify_user(sender_id: int, receiver_id: int, message: str, connected_users: dict, db: AsyncSession):
    if receiver_id not in connected_users:
        await send_notification(receiver_id, f"Вам пришло сообщение от пользователя {sender_id}: {message}", connected_users)


async def main():
    dp.include_router(router)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
