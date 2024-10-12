import boto3
from botocore.exceptions import NoCredentialsError
from config import settings
import redis
import time


conversion_status = []

MINIO_ENDPOINT =  settings.minio_hostname
MINIO_ACCESS_KEY = settings.minio_access_key
MINIO_SECRET_KEY = settings.minio_secret_key
MINIO_BUCKET = settings.minio_bucket

redis_client = redis.StrictRedis(host='192.168.1.125', port=6379, db=0)


s3 = boto3.client(
    's3',
    endpoint_url = MINIO_ENDPOINT,
    aws_access_key_id = MINIO_ACCESS_KEY,
    aws_secret_access_key = MINIO_SECRET_KEY
)

def listen_for_notification():
    while True:
        message = redis_client.xread({b'api_gateway_notifications': '$'}, count=1, block=0)
        for stream, message_data in message:
            for message_id, fields in message_data:
                message_dict = {key.decode(): value.decode() for key, value in fields.items()}
                print(message_dict)
                
                file_uuid = message_dict.get('file_uuid')
                bucket_name = message_dict.get('bucket_name')
                status = message_dict.get('status')
                
                if status == 'completed':
                    conversion_status.append(file_uuid)
                    print(f"File with UUID {file_uuid} is ready for download from bucket: {bucket_name}")
                else:
                    print(f"Received status {status} for file UUID {file_uuid}")
        time.sleep(10)
                


async def upload_file_to_minio(file_data, filename):
    file_uuid = filename.split('.')[0]
         
    try:
        file_data.seek(0)
        s3.upload_fileobj(file_data, MINIO_BUCKET, filename)
        print(f"File uploaded to minio: {filename}")
        return f"file uploaded successfully, processing conversion. file_uuid: {file_uuid}.mp3"
    except NoCredentialsError:
        raise Exception("Minio credentials not valid")

    
def download_file_from_minio(filename):
    
    try:
        file_obj = s3.get_object(Bucket=MINIO_BUCKET, Key=filename)
        return file_obj['Body'].read()
    except Exception as e:
        raise Exception(f"Error downloading file: {str(e)}")
    
    