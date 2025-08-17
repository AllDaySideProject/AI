from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from app.core.ApiResponse import Envelope, ok
from app.services.prompt import chatForTip
import json

router = APIRouter(prefix="/tip")

class TipItem(BaseModel):
    title: str
    content: str
class TipRequest(BaseModel):
    menus: List[str]

@router.post("", response_model=Envelope[List[TipItem]])
def getTip(req: TipRequest):
    try:
        system = """너는 남은 반찬을 새롭게 조리해서 먹는 법을 알려주는 식사 코치야.
출력은 반드시 하나의 JSON 객체여야 해. title에는 그에 맞는 제목을, content에는 방법을 적어주면 돼.
제목의 형식은 고정되어 있지 않아도 되고, 창의성이 돋보이는 재밌는 묘사를 이용한 제목을 지어줘. 반찬마다 다른 형식의 제목을 부탁해.
예시는 아래와 같아:
{"items":[{"title":"남은 감자볶음, 고소한 감자전으로","content":"감자볶음을 으깨서 계란과 함께 섞어 팬에 부치면 감자전이 됩니다."}, ...]}

규칙:
- 배열의 각 요소는 {"title":"...", "content":"..."} 형식
- title은 20자 이내, content는 한국어 1~2문장, 줄바꿈 없이 작성
- 코드블록/마크다운/설명 문장/문자열로 감싸기(이스케이프 따옴표) 모두 금지
"""

        user = (
            f"남은 반찬 목록: {', '.join(req.menus)}\n"
            "- 위 목록의 각 반찬마다 아이디어 1개씩 제시해줘.\n"
            '- 반드시 {"items":[...]} 형태로만 반환해.'
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        text = chatForTip(messages, temperature=0.6, max_tokens=400)

        obj = json.loads(text)
        items =  obj["items"]

        return ok(items, http_status=200) 

    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))