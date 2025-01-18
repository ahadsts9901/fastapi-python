from fastapi import APIRouter, Depends, HTTPException
from .middleware import jwt_required
from .models import Chat
from datetime import datetime
from pydantic import BaseModel
from extensions import socket

router = APIRouter()

class MessageResponse(BaseModel):
    id: str
    from_id: str
    to_id: str
    text: str
    created_at: str
    updated_at: str

class CreateMessageResponse(BaseModel):
    message: str
    data: MessageResponse

class GetMessagesResponse(BaseModel):
    message: str
    data: list[MessageResponse]

@router.post("/message", response_model=CreateMessageResponse)
async def create_message(data: dict, current_user: dict = Depends(jwt_required)):
    try:
        if not data:
            raise HTTPException(status_code=400, detail="Data is required")
        if 'to_id' not in data:
            raise HTTPException(status_code=400, detail="to_id is required")
        if 'message' not in data:
            raise HTTPException(status_code=400, detail="Text message is required")

        from_id = current_user["id"]
        to_id = data["to_id"]
        message = data["message"]

        new_message = Chat(
            from_id=from_id,
            to_id=to_id,
            text=message,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        new_message.save()

        message_data = {
            "id": str(new_message.id),
            "from_id": new_message.from_id,
            "to_id": new_message.to_id,
            "text": new_message.text,
            "created_at": new_message.created_at.isoformat(),
            "updated_at": new_message.updated_at.isoformat()
        }

        await socket.emit(f'chat-message-{to_id}', message_data)
        return {
            "message": "message sent",
            "data": message_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Internal server error", "error": str(e)})

@router.get("/messages/{to_id}", response_model=dict)
async def get_messages(to_id: str, current_user: dict = Depends(jwt_required)):
    try:
        from_id = current_user["id"]
        messages = Chat.objects(
            __raw__={
                "$or": [
                    {"from_id": from_id, "to_id": to_id},
                    {"from_id": to_id, "to_id": from_id}
                ]
            }
        ).order_by('-created_at')

        return {
            "message": "messages fetched",
            "data": [
                {
                    "id": str(msg.id),
                    "from_id": msg.from_id,
                    "to_id": msg.to_id,
                    "text": msg.text,
                    "created_at": msg.created_at.isoformat(),
                    "updated_at": msg.updated_at.isoformat()
                }
                for msg in messages
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Internal server error", "error": str(e)})

@router.put("/message/{message_id}", response_model=dict)
async def edit_message(message_id: str, data: dict, current_user: dict = Depends(jwt_required)):
    try:
        if not data or 'message' not in data:
            raise HTTPException(status_code=400, detail="Updated message text is required")

        message = Chat.objects(id=message_id, from_id=current_user["id"]).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found or unauthorized")

        message.text = data['message']
        message.updated_at = datetime.utcnow()
        message.save()

        return {"message": "Message updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Internal server error", "error": str(e)})

@router.delete("/message/{message_id}", response_model=dict)
async def delete_message(message_id: str, current_user: dict = Depends(jwt_required)):
    try:
        message = Chat.objects(id=message_id, from_id=current_user["id"]).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found or unauthorized")

        message_id = str(message.id)
        message.delete()

        room = f'message-{message.to_id}'
        await socket.emit(f'delete-chat-message-{message.to_id}', {'deletedMessageId': message_id})

        return {"message": "Message deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Internal server error", "error": str(e)})
