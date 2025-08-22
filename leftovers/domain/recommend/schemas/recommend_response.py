from typing import List, Literal, Optional
from pydantic import BaseModel, Field

Concept = Literal["diet", "keto", "low_sodium", "glycemic", "bulking"]

# 영양 성분 상세 모델
class NutritionDetail(BaseModel):
    kcal: float=0; protein: float=0; fat: float=0; carbs: float=0
    sugar: float=0; fiber: float=0; sodium: float=0; sat_fat: float=0

# 추천 항목 모델
class MatchItem(BaseModel):
    input_menu: str # 입력값
    matched_name: Optional[str] = None # 매칭된 메뉴명
    similarity: Optional[float] = None # 입력값과 매칭된 메뉴명의 유사도
    suitability: Optional[int] = None # 컨셉 적합도
    # detail: Optional[NutritionDetail] = None # 영양정보 상세 - 개발용
    # note: Optional[str] = None # 기타 메모 - 개발용

# 추천 결과 응답 DTO
class RecommendRes(BaseModel):
    concept: Concept
    count: int
    items: List[MatchItem]