from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CAMERA_INPUT: int = 0

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()

