import numpy as np
from leftovers.domain.recommend.service.scoring import compute_score
from leftovers.domain.recommend.schemas.recommend_response import MatchItem
from leftovers.domain.recommend.service import loader, matcher

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
def evaluate_items(concept: str, menus: list[str]) -> list[MatchItem]:
    matched = []
    features = []

    for menu in menus:
        idx, b_name, sim = matcher.match_top1(menu) # 메뉴 매칭
        if idx < 0:
            matched.append(MatchItem(input_menu=menu, note="매칭 실패"))
            features.append(None)
            continue
        
        b_row = dict(loader._DB_ROWS[idx]) # 음식 데이터에서 해당 행을 딕셔너리 형태로 가져옴
        b_row["name"] = b_name

        x_num = to_feat(b_row) # 피쳐 추출
        matched.append((menu, b_name, sim, b_row, idx))  # 후처리용
        features.append(x_num)
    
    valid_idx = [i for i, f in enumerate(features) if f is not None] # 매칭 실패 제거하고 batch 변환
    
    if not valid_idx:
        return matched  # 전부 실패면 그대로 반환
    
    X = loader._DB_FEATS[[m[-1] for m in matched if not isinstance(m, MatchItem)]] # dict -> numpy 변환 대신 캐시된 _DB_FEATS 사용

    X = loader._IMPUTER.transform(X) # 결측치 보간
    X = loader._SCALER.transform(X) # 모델 학습 범위에 맞게 정규화

    model = loader._MODELS[concept]
    preds = model.predict(X) # 모델 배치 예측

    results = []
    pred_i = 0
    for m in matched:
        if isinstance(m, MatchItem):  # 매칭 실패
            results.append(m)
        else:
            menu, b_name, sim, b_row, idx = m
            pred = float(preds[pred_i])
            rule = float(compute_score(concept, b_row, loader._CALIB or None))
            fused = 0.3 * pred + 0.7 * rule
            score_int = int(round(fused))
            pred_i += 1

            results.append(
                MatchItem(
                    input_menu=menu,
                    matched_name=b_name,
                    similarity=round(sim, 3),
                    suitability=score_int,
                )
            )
    return results
