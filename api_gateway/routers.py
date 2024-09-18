from fastapi import APIRouter, Header, File, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse
import services
from io import BytesIO
import uuid
from auth_utils import *
import redis
from config import settings
import asyncio
import threading
from services import listen_for_notification



router = APIRouter()

redis_client = redis.StrictRedis(host='192.168.1.125', port=6379, db=0)

def push_to_stream(stram_name, message):
    redis_client.xadd(stram_name, message)

@router.post("/convertor/upload")
async def upload_file(file: UploadFile = File(...), authorization: str = Header(None)):

    
    user_id = await get_verified_user(authorization)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User verification failed"
        )
    file_uuid = str(uuid.uuid4())
    filename = f"{file_uuid}.mp4"
    
    redis_message = {
        'file_uuid': file_uuid,
        'bucket_name': settings.minio_bucket
    }
    
    push_to_stream('conversion_requests', redis_message)
    file_url = await services.upload_file_to_minio(file.file, filename)
    return {
        "message": file_url
    }



@router.get("/convertor/get")
async def download_file(filename: str):
    try:
        file_data = services.download_file_from_minio(filename)
        return StreamingResponse(BytesIO(file_data), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
 
 
@router.on_event("startup")
async def startup_event():
    notification_thread = threading.Thread(target=listen_for_notification, daemon=True)
    notification_thread.start()