from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User,Message
from app.schemas import UserCreate,MessageCreate
from passlib.context import CryptContext
from sqlalchemy.future import select


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_username(db: AsyncSession, username: str):
    query = select(User).filter(User.username == username)
    result = await db.execute(query)
    return result.scalars().first()


async def create_message(db: AsyncSession, message: MessageCreate):
    db_message = Message(
        content=message.content,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message


async def get_all_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_messages_between_users(db: AsyncSession, sender_id: int, receiver_id: int):
    result = await db.execute(select(Message).where(
        ((Message.sender_id == sender_id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == sender_id))
    ))
    return result.scalars().all()


async def update_user_telegram_id(db: AsyncSession, user_id: int, telegram_id: int):
    user = await get_user_by_id(db, user_id)
    if user:
        user.telegram_id = telegram_id
        await db.commit()
