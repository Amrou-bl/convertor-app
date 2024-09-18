from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    minio_hostname: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    
    class Config:
        env_file = ".env"
        

settings = Settings()
        