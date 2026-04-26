import os
from enum import Enum
from pathlib import Path
from dotenv import load_dotenv

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"

def get_environment() -> Environment:
    match os.getenv("APP_ENV", "development").lower():
        case "production" | "prod":
            return Environment.PRODUCTION
        case "staging" | "stage":
            return Environment.STAGING
        case "test":
            return Environment.TEST
        case _:
            return Environment.DEVELOPMENT

def load_env_file():
    env = get_environment()
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    env_files = [
        os.path.join(base_dir, f".env.{env.value}.local"),
        os.path.join(base_dir, f".env.{env.value}"),
        os.path.join(base_dir, ".env.local"),
        os.path.join(base_dir, ".env"),
    ]

    for env_file in env_files:
        if os.path.isfile(env_file):
            load_dotenv(dotenv_path=env_file)
            return env_file
    return None

ENV_FILE = load_env_file()

class Settings:
    def __init__(self):
        self.ENVIRONMENT = get_environment()
        self.PROJECT_NAME = os.getenv("PROJECT_NAME", "Liaison-Spark API")
        self.VERSION = os.getenv("VERSION", "1.0.0")
        self.DESCRIPTION = os.getenv("DESCRIPTION", "Autonomous Big Data Analyst & PySpark Generator")
        self.API_V1_STR = os.getenv("API_V1_STR", "/api")
        
        self.WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", "127.0.0.1")
        self.WEAVIATE_PORT = os.getenv("WEAVIATE_PORT", "8080")
        self.WEAVIATE_GRPC_PORT = os.getenv("WEAVIATE_GRPC_PORT", "50051")
        
        self.LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
        self.LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
        self.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)

settings = Settings()