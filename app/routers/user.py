from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, auth
from app.database.database import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas import UserCreate

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register")
async def register(username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    user = UserCreate(username=username, password=password)
    db_user = await crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await crud.create_user(db, user)


@router.post("/token")
async def login(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await crud.get_user_by_username(db, form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
