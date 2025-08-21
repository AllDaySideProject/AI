from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_absolute_error
from sklearn.impute import SimpleImputer

from app.domain.recommend.service.food_kfda_loader import load_kfda_excels
from app.domain.recommend.service.scoring import fit_calibration, compute_score

FOOD_FILES = ["app/domain/recommend/data/foodData1.xlsx", "app/domain/recommend/data/foodData2.xlsx"]
MODEL_DIR = Path("app/domain/recommend/model_store")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# 컨셉
CONCEPTS = ["diet", "keto", "low_sodium", "glycemic", "bulking"]

# 음식 딕셔너리를 벡터로 변환
def _to_feat(n: dict) -> np.ndarray:
    kcal    = float(n.get("kcal", 0.0))
    protein = float(n.get("protein", 0.0))
    fat     = float(n.get("fat", 0.0))
    carbs   = float(n.get("carbs", 0.0))
    sugar   = float(n.get("sugar", 0.0))
    fiber   = float(n.get("fiber", 0.0))
    sodium  = float(n.get("sodium", 0.0))  # mg / 100g
    sat_fat = float(n.get("sat_fat", fat))
    netcarb = max(carbs - fiber, 0.0) # 순탄수 (탄수 - 식이섬유)
    return np.array([kcal, protein, fat, carbs, sugar, fiber, sodium, sat_fat, netcarb], dtype=float)

def main():
    # 데이터 로드
    rows = load_kfda_excels(FOOD_FILES, sheet_name=None)
    if not rows:
        raise SystemExit("데이터 엑셀을 찾지 못했거나 로드 실패")

    # 이름 리스트
    names = [str(r.get("name","")) for r in rows]

    # 음식명을 글자 단위로 벡터화 -> 이름이 비슷하면 높은 유사도 부여
    name_vec = TfidfVectorizer(analyzer="char", ngram_range=(2, 5), min_df=1)
    X_name = name_vec.fit_transform(names) # 음식 이름 특징 벡터

    # 모든 음식을 수치 벡터로 변환
    X_num = np.vstack([_to_feat(r) for r in rows])

    imputer = SimpleImputer(strategy="median")
    X_imp = imputer.fit_transform(X_num) # 결측치를 중앙값으로 채움
    scaler = StandardScaler()
    X = scaler.fit_transform(X_imp) # 음식 수치 벡터 정규화 (각 열의 평균 = 0, 표준편차 = 1이 되도록 변환)

    calib = fit_calibration(rows) # 데이터로 분위수 기준값 계산 -> 규칙 점수표 생성
    joblib.dump(calib, MODEL_DIR / "calibration.joblib")

    for concept in CONCEPTS:
        # 특정 음식이 해당 컨셉에 얼마나 적합한지 규칙 기반 점수로 계산
        y = np.array([compute_score(concept, r, calib) for r in rows], dtype=float)

        # 릿지 회귀 중 교차 검증 -> 여러 개 후보값을 두고, 데이터 나눠서 성능 제일 좋은 값을 자동으로 찾아줌
        model = RidgeCV(alphas=(0.1, 1.0, 3.0, 10.0, 30.0), # 규제 강도 : 과적합 방지
                        cv=5, scoring="neg_mean_absolute_error")
        model.fit(X, y) # X와 y 관계 학습 (이 정도 영양성분이면 이 컨셉 점수는 나와야 한다!)
        pred = model.predict(X) # 학습된 모델로 X 데이터를 다시 넣어 예측 -> 훈련 데이터에 대해 얼마나 잘 맞췄나 확인
        mae = mean_absolute_error(y, pred) # 실제 점수(y)와 예측 점수(pred)의 차이를 MAE(평균 절대 오차)로 계산
        
        print(f"[{concept}] 교차검증을 통한 최적 알파 값 ={model.alpha_:.2f}  평균 절대 오차={mae:.2f}") 
        joblib.dump(model, MODEL_DIR / f"concept_model_{concept}.joblib")

    # 아티팩트 저장
    joblib.dump(name_vec, MODEL_DIR / "name_vectorizer.joblib")
    joblib.dump(X_name,  MODEL_DIR / "name_matrix.joblib")
    joblib.dump(names,   MODEL_DIR / "name_list.joblib")
    joblib.dump(imputer, MODEL_DIR / "nutrition_imputer.joblib")
    joblib.dump(scaler,  MODEL_DIR / "nutrition_scaler.joblib")

    print("모델 저장 완료 : ", MODEL_DIR.resolve())

if __name__ == "__main__":
    main()
