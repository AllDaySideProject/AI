from fastapi import APIRouter
from leftovers.core.response.api_response import Envelope, ok, fail
from leftovers.domain.recommend.schemas.recommend_request import RecommendReq
from leftovers.domain.recommend.schemas.recommend_response import RecommendRes
from leftovers.domain.recommend.service import evaluator, loader

import time

router = APIRouter(prefix="/menus")

@router.post("/recommend", response_model=Envelope[RecommendRes])
def recommend(req: RecommendReq):
    start = time.time()
    if not loader._DB_ROWS: # DB, 모델이 안 불러와졌으면 500 에러
        return fail(500, {"message": "DB/모델이 비어있습니다."}).model_dump()
    if req.concept not in loader.CONCEPTS: # 컨셉명이 올바르지 않으면 400 에러
        return fail(400, {"message": f"알 수 없는 컨셉: {req.concept}"}).model_dump()
    
    after_load = time.time()

    # 요청 메뉴를 돌면서 evaluate_items 호출
    items = evaluator.evaluate_items(req.concept, req.items)

    after_evaluate = time.time()

    ranked = [r for r in items if r.matched_name] # 이름이 매칭되지 않으면 제외
    ranked.sort(key=lambda r: (r.suitability, r.similarity), reverse=True) # 적합도와 유사도가 높은 순으로 정렬
    topn = ranked[: max(1, int(req.count))] # 요청한 개수만큼만 반환
    after_ranked = time.time()

    res = RecommendRes(concept=req.concept, count=len(topn), items=topn)

    print(f"[DEBUG] 0. start {(start):.3f}s")
    print(f"[DEBUG] 1. Loader check took {(after_load):.3f}s")
    print(f"[DEBUG] 2. Evaluation took {(after_evaluate):.3f}s")
    print(f"[DEBUG] 3. Ranking took {(after_ranked):.3f}s")

    return ok(res)
