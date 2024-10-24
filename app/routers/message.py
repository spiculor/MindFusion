from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas import MessageCreate
from app import crud
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app import auth


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


connected_users = {}


@router.websocket("/ws/{receiver_id}")
async def websocket_endpoint(websocket: WebSocket, receiver_id: int, token: str = Query(...), db: AsyncSession = Depends(get_db)):
    try:
        await websocket.accept()
        credentials_exception = HTTPException(
            status_code=403, detail="Could not validate credentials"
        )
        user = await auth.get_current_user(token, db)
        sender_id = user.id

        while True:
            data = await websocket.receive_text()
            message_data = MessageCreate(
                content=data,
                sender_id=sender_id,
                receiver_id=receiver_id
            )
            await crud.create_message(db, message_data)

            for uid, conn in connected_users.items():
                if uid == receiver_id or uid == sender_id:
                    await conn.send_text(f"User {sender_id}: {data}")
    except WebSocketDisconnect:
        connected_users.pop(sender_id, None)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        await websocket.close(code=1000)


@router.get("/chat")
async def choose_user(request: Request, db: AsyncSession = Depends(get_db)):
    users = await crud.get_all_users(db)
    return templates.TemplateResponse("choose_user.html", {"request": request, "users": users})


@router.get("/chat/{user_id}")
async def get_chat(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    users = await crud.get_all_users(db)
    selected_user = await crud.get_user_by_id(db, user_id)
    
    if not selected_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    messages = await crud.get_messages_between_users(db, 1, user_id)

    return templates.TemplateResponse("chat.html", {
        "request": request,
        "users": users,
        "selected_user": selected_user,
        "messages": messages
    })