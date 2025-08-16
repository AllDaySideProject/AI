from openai import OpenAI
from app.core.config import settings # 환경설정 로더 가져오기

_cfg = settings() # settings

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=_cfg["openai_api_key"])


def chat_sync(messages, model=None, **kwargs) :
    model = model or _cfg["openai_model"]

    # OpenAI API에 대화 내용 보내기
    res = client.responses.create(
        model=model, # 사용할 모델
        input=messages, # 대화 내용
        **kwargs # 추가 옵션
    )

    # 응답에서 텍스트만 꺼내서 반환
    return res.output.text
