from fastapi import APIRouter, HTTPException
from . import services
from rich import print
import os

router = APIRouter()




@router.post("/convert")
async def convert_video_to_mp3(bucket_name: str, file_uuid: str):
    
    local_input_file = os.path.join("downloaded_files", f"{file_uuid}.mp4")
    local_output_file = os.path.join("downloaded_files", f"{file_uuid}.mp3")
    
    try:
        
        if not os.path.exists("downloaded_files"):
            os.mkdir("downloaded_files")

        
        services.download_file_from_minio(f"{file_uuid}.mp4", local_input_file)
        
        if not os.path.exists(local_input_file):
            raise HTTPException(status_code=404, detail="Downloaded file not found")

        services.convert_to_mp3(local_input_file, local_output_file)
        

        services.upload_file(bucket_name, f"{file_uuid}.mp3", local_output_file)
        
        
        os.remove(local_input_file)
        os.remove(local_output_file)
        return {"message": "File downloaded successfully", "file_name": file_uuid}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))