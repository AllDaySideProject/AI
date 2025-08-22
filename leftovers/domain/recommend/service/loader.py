from typing import List
import joblib

from leftovers.domain.recommend.service.food_kfda_loader import load_kfda_excels

FOOD_FILES = ["leftovers/domain/recommend/data/foodData1.xlsx", "leftovers/domain/recommend/data/foodData2.xlsx"]
MODEL_DIR = "leftovers/domain/recommend/model_store"

# 컨셉
CONCEPTS = {"diet", "keto", "low_sodium", "glycemic", "bulking"}

# 캐시 이용 -> 서버 시작 시, 메모리에 로딩해두고 API 요청마다 바로 쓰게
_DB_ROWS: List[dict] = [] # 음식 데이터
_NAME_LIST: List[str] = [] # 음식 이름 리스트
_NAME_VEC = None # 음식 이름 벡터화(음식 이름 문자열을 숫자 벡터로 변환)
_NAME_MAT = None # 벡터화 결과 저장소(매트릭스)
_IMPUTER = None # 결측치를 적절한 값으로 채워주는 보간기
_SCALER = None # 값들의 크기를 일정한 값으로 맞춰주는 도구
_MODELS = {} # 컨셉별 ML 모델
_CALIB = None # 점수 보정기


# 캐시에 DB와 모델 전부 로딩
def load_all():
    global _DB_ROWS, _NAME_LIST, _NAME_VEC, _NAME_MAT, _IMPUTER, _SCALER, _MODELS, _CALIB
    
    _DB_ROWS = load_kfda_excels(FOOD_FILES, sheet_name=None)

    _NAME_VEC = joblib.load(f"{MODEL_DIR}/name_vectorizer.joblib")
    _NAME_MAT = joblib.load(f"{MODEL_DIR}/name_matrix.joblib")
    _NAME_LIST = joblib.load(f"{MODEL_DIR}/name_list.joblib")


    _IMPUTER = joblib.load(f"{MODEL_DIR}/nutrition_imputer.joblib")
    _SCALER  = joblib.load(f"{MODEL_DIR}/nutrition_scaler.joblib")

    _MODELS = {c: joblib.load(f"{MODEL_DIR}/concept_model_{c}.joblib") for c in CONCEPTS}

    try:
        _CALIB = joblib.load(f"{MODEL_DIR}/calibration.joblib")
    except Exception:
        _CALIB = None
