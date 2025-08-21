from typing import List, Literal
from pydantic import BaseModel, Field

Concept = Literal["diet", "keto", "low_sodium", "glycemic", "bulking"]

# 추천 요청 dto
class RecommendReq(BaseModel):
    concept: Concept # 컨셉
    count: int = Field(15, ge=1, le=100) # 수량 : 기본값 15 / 최소 1, 최대 100
    items: List[str] # 메뉴 이름 목록