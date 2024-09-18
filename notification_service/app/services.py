from fastapi import HTTPException
from schemas import *
import redis
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "amroubl126@gmail.com"
SMTP_PASSWORD = "@madara666"

redis_client = redis.StrictRedis(host='192.168.1.125', port=6379, db=0)

def send_notification(stream_name, message):
    redis_client.xadd(stream_name, message)  


def read_massge():
    while True:
        message = redis_client.xread({b'notification_message': '$'}, count=1, block=0)
        for stream, message_data in message:
            for message_id, fields in message_data:
                
                message_dict = {key.decode(): value.decode() for key, value in fields.items()}
                
                print(message_dict)
                
                file_uuid = message_dict.get('file_uuid')
                bucket_name = message_dict.get('bucket_name')
                
                api_gateway_message = {
                    'file_uuid': file_uuid,
                    'bucket_name': bucket_name,
                    'status': 'completed'
                }
                
                send_notification('api_gateway_notifications', api_gateway_message)
       