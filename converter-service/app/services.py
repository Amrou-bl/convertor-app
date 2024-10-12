import boto3
import subprocess
from config import settings
import redis
import os
import time


redis_client = redis.StrictRedis(host='192.168.1.125', port=6379, db=0)


MINIO_ENDPOINT =  settings.minio_hostname
MINIO_ACCESS_KEY = settings.minio_access_key
MINIO_SECRET_KEY = settings.minio_secret_key
MINIO_BUCKET = settings.minio_bucket

s3_client = boto3.client(
    's3',
    endpoint_url = MINIO_ENDPOINT,
    aws_access_key_id = MINIO_ACCESS_KEY,
    aws_secret_access_key = MINIO_SECRET_KEY
)


def list_bucket_objects():
        response = s3_client.list_objects_v2(Bucket=MINIO_BUCKET)
        print(f"Objects in bucket '{MINIO_BUCKET}':")
        for obj in response.get('Contents', []):
            print(obj['Key'])
    
    
def download_file_from_minio(filename, local_path):
    try:
        # Debug: List all objects in the bucket

        list_bucket_objects()
        
        # Fetch the file object from MinIO
        #test_key = 'd025df5b-1dd8-47e0-b853-474bb22d4dc6.mp4'
        file_obj = s3_client.get_object(Bucket=MINIO_BUCKET, Key=filename)
        
        # Write the file to the local path
        with open(local_path, 'wb') as file_data:
            file_data.write(file_obj['Body'].read())
        
        print(f"File {filename} successfully downloaded to {local_path}")
    
    except Exception as e:
        raise Exception(f"Error downloading file from MinIO: {str(e)}")

   
def convert_to_mp3(input_file, output_file):
    
    ffmpeg_executable = r"D:\ffmpeg\ffmpeg-2024-07-24-git-896c22ef00-full_build\bin\ffmpeg.exe"
    try:
        command = [ffmpeg_executable,"-i",input_file,output_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            raise Exception(f"Converion failed: {result.stderr.decode()}")
        
    except subprocess.CalledProcessError as e:
        print (f"Error during conversion: {e}")
        
        
def upload_file(bucket_name, file_uuid, local_path):
    s3_client.upload_file(local_path, bucket_name, file_uuid)
    


def send_notification(stream_name, message):
    redis_client.xadd(stream_name, message)


def process_conversion_requests():
    while True:
        # Read from the Redis stream
        messages = redis_client.xread({b'conversion_requests': '$'}, count=1, block=0)
        for stream, message_data in messages:
            for message_id, fields in message_data:
                # Convert fields from bytes to string
                message_dict = {key.decode(): value.decode() for key, value in fields.items()}
                print(f"Redis message: {message_dict}")
                # Extract file UUID and bucket name
                file_uuid = message_dict.get('file_uuid')
                bucket_name = message_dict.get('bucket_name')
                
                # Define local file paths
                local_input_file = os.path.join("downloaded_files", f"{file_uuid}.mp4")
                local_output_file = os.path.join("downloaded_files", f"{file_uuid}.mp3")
                
                file_name = f"{file_uuid}.mp4"
                
                try:
                    # Log file paths and bucket name
                    print(f"Attempting to download file with key: {file_name}")
                    
                    # Download, convert, and upload the file
                    time.sleep(2)
                    download_file_from_minio(file_name, local_input_file)
                    print(f"File {file_uuid}.mp4 downloaded successfully")
                    
                    print(f"Converting {local_input_file} to {local_output_file}")
                    convert_to_mp3(local_input_file, local_output_file)
                    print(f"File {file_uuid}.mp4 converted to {local_output_file}")
                    
                    print(f"Uploading {local_output_file} to bucket {bucket_name}")
                    upload_file(bucket_name, f"{file_uuid}.mp3", local_output_file)
                    print(f"File {file_uuid}.mp3 uploaded successfully")
                    
                    redis_message = {
                        'file_uuid': file_uuid,
                        'bucket_name': MINIO_BUCKET
                    }
                    
                    send_notification('notification_message', redis_message)
                except Exception as e:
                    print(f"Error processing file {file_name}: {str(e)}")
                finally:
                    # Clean up local files
                    if os.path.exists(local_input_file):
                        os.remove(local_input_file)
                    if os.path.exists(local_output_file):
                        os.remove(local_output_file)

        # Wait for 5 seconds before the next iteration
        time.sleep(5)



