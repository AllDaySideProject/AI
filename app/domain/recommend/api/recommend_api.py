from fastapi import APIRouter
from app.core.response.api_response import Envelope, ok, fail
from app.domain.recommend.schemas.recommend_request import RecommendReq
from app.domain.recommend.schemas.recommend_response import RecommendRes
from app.domain.recommend.service import evaluator, loader

router = APIRouter(prefix="/menus")

@router.post("/recommend", response_model=Envelope[RecommendRes])
def recommend(req: RecommendReq):
    if not loader._DB_ROWS: # DB, 모델이 안 불러와졌으면 500 에러
        return fail(500, {"message": "DB/모델이 비어있습니다."}).model_dump()
    if req.concept not in loader.CONCEPTS: # 컨셉명이 올바르지 않으면 400 에러
        return fail(400, {"message": f"알 수 없는 컨셉: {req.concept}"}).model_dump()

    # 요청 메뉴를 돌면서 evaluate_item 호출
    items = [evaluator.evaluate_item(req.concept, a) for a in req.items]
    ranked = [r for r in items if r.matched_name] # 이름이 매칭되지 않으면 제외
    ranked.sort(key=lambda r: (r.suitability, r.similarity), reverse=True) # 적합도와 유사도가 높은 순으로 정렬
    topn = ranked[: max(1, int(req.count))] # 요청한 개수만큼만 반환

    res = RecommendRes(concept=req.concept, count=len(topn), items=topn)
    return ok(res)
