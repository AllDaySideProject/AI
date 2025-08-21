import numpy as np
from app.domain.recommend.service.scoring import compute_score
from app.domain.recommend.schemas.recommend_response import MatchItem
from app.domain.recommend.service import loader, matcher

# 음식 영양 성분을 딕셔너리에서 numpy 배열로 변환(ML 모델 입력은 항상 숫자여야 하므로)
def to_feat(n: dict) -> np.ndarray:
    kcal    = float(n.get("kcal", 0.0))
    protein = float(n.get("protein", 0.0))
    fat     = float(n.get("fat", 0.0))
    carbs   = float(n.get("carbs", 0.0))
    sugar   = float(n.get("sugar", 0.0))
    fiber   = float(n.get("fiber", 0.0))
    sodium  = float(n.get("sodium", 0.0))
    sat_fat = float(n.get("sat_fat", fat))
    netcarb = max(carbs - fiber, 0.0)
    return np.array([kcal, protein, fat, carbs, sugar, fiber, sodium, sat_fat, netcarb], dtype=float)

# 데이터에서 유사한 메뉴 찾아 점수를 계산하여 반환
def evaluate_item(concept: str, menu: str):
    idx, b_name, sim = matcher.match_top1(menu) # 입력 메뉴명과 가장 유사한 메뉴 찾기

    if idx < 0:
        return MatchItem(input_menu=menu, note="매칭 실패")

    b_row = dict(loader._DB_ROWS[idx]) # 음식 데이터에서 해당 행을 딕셔너리 형태로 가져옴
    b_row["name"] = b_name

    x_num = to_feat(b_row).reshape(1, -1) # 영양성분을 숫자 벡터로 변환
    x_imp = loader._IMPUTER.transform(x_num) # 결측치 보간
    x_scaled = loader._SCALER.transform(x_imp) # 모델 학습 범위에 맞게 정규화

    model = loader._MODELS[concept]
    pred = float(model.predict(x_scaled)[0])  # 모델이 예측한 적합도
    rule = float(compute_score(concept, b_row, loader._CALIB or None)) # 규칙 기반 점수
    fused = 0.3 * pred + 0.7 * rule
    score_int = int(round(fused)) # 최종 점수

    def nz(v):
        try:
            x = float(v) # NaN, inf 같은 값 들어오면 0.0 보정
            return 0.0 if not np.isfinite(x) else x
        except Exception:
            return 0.0

    return MatchItem(
        input_menu=menu,
        matched_name=b_name,
        similarity=round(sim, 3),
        suitability=score_int
        # detail=NutritionDetail( # 개발 시에만 반환
        #    kcal=nz(b_row.get("kcal")), protein=nz(b_row.get("protein")), fat=nz(b_row.get("fat")),
        #    carbs=nz(b_row.get("carbs")), sugar=nz(b_row.get("sugar")), fiber=nz(b_row.get("fiber")),
        #    sodium=nz(b_row.get("sodium")), sat_fat=nz(b_row.get("sat_fat", b_row.get("fat", 0.0)))
        # ),
        # note=None
    )