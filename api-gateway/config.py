from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    
    minio_hostname: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    
    class Config:
        env_file = ".env"
        

settings = Settings()
        