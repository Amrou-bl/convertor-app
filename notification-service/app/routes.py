from fastapi import APIRouter
from services import *
from schemas import Notification
router = APIRouter()


@router.post("/notify")
async def notify_user(notification: Notification):
    try:
        subject = "File ready to download"
        body = f"Your file with UUID {notification.file_uuid} has been successfylly converted and is ready to download. \n\nMessage: {notification.message}"
        
        return {"status": "Notification sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
        
        
        
        
        
        
        
        
