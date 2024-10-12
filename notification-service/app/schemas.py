from pydantic import BaseModel


class Notification(BaseModel):
    user_email: str
    file_uuid: str
    message: str
    