import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "SecureAgent AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    MAX_PAYLOAD_SIZE_BYTES: int = 1024 * 1024  # 1 MB
    DEFAULT_MODEL_MODE: str = os.getenv("DEFAULT_MODEL_MODE", "deterministic")  # deterministic | ollama | ibm_z_enclave
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3:8b")
    CORS_ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    ENABLE_TAMPER_EVIDENT_HASHING: bool = True
    IBM_Z_EMULATION_MODE: bool = True  # Clean fallback when s390x hardware is not present

settings = Settings()
