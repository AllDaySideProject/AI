# 알뜰 식사 TIP 응답 API

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from app.services.openAIClient import client
from app.core.config import settings

router = APIRouter(prefix="/tip")

class Msg(BaseModel):
    role: Literal["user", "system", "assistant"] # 메시지를 보낸 주체
    content : str # 메시지 텍스트


class ChatBody(BaseModel):
    messages: List[Msg] # 대화 전체
    model : str | None = None # 모델 종류
    temperature : float | None = 0.7 # 창의성 정도 (기본 0.7)
    max_output_tokens : int | None = None # 최대 응답 길이

@router.post("")
def chat(body: ChatBody):
    try:
        res = client.responses.create(
            model=body.model or settings()["openai_model"],
            input=[m.model_dump() for m in body.messages], # 메시지 변환
            temperature=body.temperature,
            max_output_tokens=body.max_output_tokens
        )

        return {"text": res.output_text} # 결과 텍스트만 반환
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))