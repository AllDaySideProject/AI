from __future__ import annotations
from typing import List, Optional, Dict, Any
import math
import pandas as pd
import numpy as np

# 컬럼 매핑
COL = {
    "name": "식품명",
    "kcal": "에너지(kcal)",
    "protein": "단백질(g)",
    "fat": "지방(g)",
    "carbs": "탄수화물(g)",
    "sugar": "당류(g)",
    "fiber": "식이섬유(g)",
    "sodium": "나트륨(mg)",
    "sat_fat": "포화지방산(g)",
}

# 숫자형 컬럼
NUM_COLS = [
    "kcal","protein","fat","carbs","sugar","fiber","sodium","sat_fat"
]

# 데이터 전처리  -> float형으로 변환
def _to_float(x, default=np.nan):
    try:
        if x is None: return default # None이면 default 값 반환

        if isinstance(x, str): # str이면
            x = x.strip().replace(",", "") # 앞뒤 공백,쉼표를 없앰
            if x == "": return default # 비어있으면 default 값 반환
        v = float(x)

        if math.isfinite(v): return v # 유한한 값일 경우 해당 값 반환
    except Exception:
        pass
    return default


# 행 데이터 -> 딕셔너리
def _row_to_dict(row: pd.Series) -> Dict[str, Any]: # pandas의 행을 받아 딕셔너리로 변환
    dic = {
        "name": str(row.get(COL["name"], "")).strip(),
        "kcal": _to_float(row.get(COL["kcal"])),
        "protein": _to_float(row.get(COL["protein"])),
        "fat": _to_float(row.get(COL["fat"])),
        "carbs": _to_float(row.get(COL["carbs"])),
        "sugar": _to_float(row.get(COL["sugar"])),
        "fiber": _to_float(row.get(COL["fiber"])),
        "sodium": _to_float(row.get(COL["sodium"])),
        "sat_fat": _to_float(row.get(COL["sat_fat"])),
    }

    return dic


# 엑셀 파일을 읽어 리스트로 변환
def load_kfda_excels(
    files: List[str], # 파일 경로
    sheet_name: Optional[str] = None # 시트명
) -> List[dict]:
    rows: List[dict] = [] # 데이터를 담을 공간
    for path in files:
        xls = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
        if isinstance(xls, dict): # 엑셀에 시트가 여러개라면
            frames = [df for _, df in xls.items()]
            df = pd.concat(frames, ignore_index=True)  # 모든 시트의 데이터를 하나로 합치기
        else:
            df = xls

        out = [_row_to_dict(r) for _, r in df.iterrows()] # 데이터 프레임의 각 행을 딕셔너리로 변환
        rows.extend(out)

    rows = [r for r in rows if r.get("name")] # 식품명이 있는 행만 가져오기

    cleaned = []
    for r in rows:
        # 해당 해의 NUM_COLS의 값 중 유효한 값이 하나라도 있으면 해당 행을 cleaned 딕셔너리에 추가
        has_any = any(np.isfinite(r.get(k, np.nan)) for k in NUM_COLS)
        if has_any:
            cleaned.append(r)
    return cleaned