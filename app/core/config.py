import os # 환경변수 읽어올 수 있도록 os 모델 임포트
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

@lru_cache # settings() 함수에 붙여 환경변수 값을 계속 유지
def settings():
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "openai_base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "timeout_s": float(os.getenv("OPENAI_TIMEOUT_S", "60")),
    }