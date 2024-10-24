from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str

class Message(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str

class UserBase(BaseModel):
    username: str
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdateTelegramId(BaseModel):
    telegram_id: Optional[int] = None  

class User(UserBase):
    id: int
    telegram_id: Optional[int]  

    class Config:
        from_attributes = True




















