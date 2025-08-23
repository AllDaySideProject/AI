from typing import List
import joblib
import numpy as np
import hnswlib

from leftovers.domain.recommend.service.food_kfda_loader import load_kfda_excels
from leftovers.domain.recommend.service.evaluator import to_feat

FOOD_FILES = ["leftovers/domain/recommend/data/foodData1.xlsx", "leftovers/domain/recommend/data/foodData2.xlsx"]
MODEL_DIR = "leftovers/domain/recommend/model_store"

# 컨셉
CONCEPTS = {"diet", "keto", "low_sodium", "glycemic", "bulking"}

# 캐시 이용 -> 서버 시작 시, 메모리에 로딩해두고 API 요청마다 바로 쓰게
_DB_ROWS: List[dict] = [] # 음식 데이터
_DB_FEATS = None # numpy 캐시
_NAME_LIST: List[str] = [] # 음식 이름 리스트
_NAME_VEC = None # 음식 이름 벡터화(음식 이름 문자열을 숫자 벡터로 변환)
_NAME_MAT = None # 벡터화 결과 저장소(매트릭스) : 유사도 계산 전체 돌릴 때 사용
_NAME_LOOKUP = {} # 벡터화 결과 딕셔너리 : 메뉴가 DB에 있는 경우, 그 벡터만 필요할 때 사용
_IMPUTER = None # 결측치를 적절한 값으로 채워주는 보간기
_SCALER = None # 값들의 크기를 일정한 값으로 맞춰주는 도구
_MODELS = {} # 컨셉별 ML 모델
_CALIB = None # 점수 보정기

_HNSW_INDEX = None # ANN 인덱스

# 캐시에 DB와 모델 전부 로딩
def load_all():
    global _DB_ROWS, _DB_FEATS
    global _NAME_LIST, _NAME_VEC, _NAME_MAT, _NAME_LOOKUP
    global _IMPUTER, _SCALER, _MODELS, _CALIB
    
    _DB_ROWS = load_kfda_excels(FOOD_FILES, sheet_name=None)

    feats = [to_feat(row) for row in _DB_ROWS]  # dict -> numpy 변환을 미리해두기
    _DB_FEATS = np.vstack(feats).astype(np.float32) # float32로 메모리 최적화

    # 이름 벡터 관련
    _NAME_VEC = joblib.load(f"{MODEL_DIR}/name_vectorizer.joblib")
    _NAME_MAT = joblib.load(f"{MODEL_DIR}/name_matrix.joblib")
    _NAME_LIST = joblib.load(f"{MODEL_DIR}/name_list.joblib")
    _NAME_LOOKUP = {name: vec for name, vec in zip(_NAME_LIST, _NAME_MAT)}

    # HNSW 인덱스 구축
    dim = _NAME_MAT.shape[1]
    _HNSW_INDEX = hnswlib.Index(space='cosine', dim=dim)
    _HNSW_INDEX.init_index(max_elements=_NAME_MAT.shape[0],
                           ef_construction=200, M=16)
    _HNSW_INDEX.add_items(_NAME_MAT.astype(np.float32))
    _HNSW_INDEX.set_ef(50)

    # 영양성분 전처리기
    _IMPUTER = joblib.load(f"{MODEL_DIR}/nutrition_imputer.joblib")
    _SCALER  = joblib.load(f"{MODEL_DIR}/nutrition_scaler.joblib")

    # ML 모델
    _MODELS = {c: joblib.load(f"{MODEL_DIR}/concept_model_{c}.joblib") for c in CONCEPTS}

    try:
        _CALIB = joblib.load(f"{MODEL_DIR}/calibration.joblib") # calibration 로딩
    except Exception:
        _CALIB = None
