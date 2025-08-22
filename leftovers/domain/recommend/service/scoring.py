from __future__ import annotations
import re
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional

# v를 low~high 범위로 자르기
def _clip(v, low, high):
    return float(np.minimum(np.maximum(v, low), high))

# v를 float으로 변환
def _safe(v, default=0.0):
    try:
        x = float(v)
        if np.isfinite(x):
            return x
    except Exception:
        pass
    return default # None, NaN, str은 기본값 반환

# 순탄수 계산 (탄수 - 식이섬유)
def _net_carb(carbs, fiber):
    return max(_safe(carbs) - _safe(fiber), 0.0)

# 비율 계산
def _ratio(n, d, default=0.0):
    n = _safe(n); d = _safe(d)
    return default if d <= 0 else n / d # 분모가 0이면 default 반환


# 국물류
_SOUP_RE = re.compile(r"(국|탕|찌개|전골|해장국|국밥)")

# 영양 성분 항목을 담는 데이터 클래스
@dataclass
class Calib:
    q: Dict[str, Dict[str, float]]

# 영양 성분 항목들
DEFAULT_KEYS = [
    "kcal","protein","fat","carbs","sugar","fiber","sodium","sat_fat","netcarb",
    "prot_density","fat_density","carb_density","sat_ratio"
]

# 음식 데이터셋 전체를 보고 각 영양소 값들의 분위수를 계산
def fit_calibration(rows: List[dict]) -> Calib:
    arr = {k: [] for k in DEFAULT_KEYS}
    for r in rows:
        kcal    = _safe(r.get("kcal"))
        protein = _safe(r.get("protein"))
        fat     = _safe(r.get("fat"))
        carbs   = _safe(r.get("carbs"))
        sugar   = _safe(r.get("sugar"))
        fiber   = _safe(r.get("fiber"))
        sodium  = _safe(r.get("sodium"))
        sat     = _safe(r.get("sat_fat", fat))
        netc    = _net_carb(carbs, fiber)
        prot_d = _ratio(protein, kcal)   # 단백질 밀도
        fat_d  = _ratio(fat, kcal)       # 지방 밀도
        carb_d = _ratio(carbs, kcal)     # 탄수화물 밀도
        sat_r  = _ratio(sat, max(fat, 1e-9)) # 포화지방 비율


        vals = {
            "kcal":kcal, "protein":protein, "fat":fat, "carbs":carbs, "sugar":sugar,
            "fiber":fiber, "sodium":sodium, "sat_fat":sat, "netcarb":netc,
            "prot_density":prot_d, "fat_density":fat_d, "carb_density":carb_d,
            "sat_ratio":sat_r
        }

        for k, v in vals.items():
            if np.isfinite(v):
                arr[k].append(v) # arr에 키 별 값들 저장

    q = {}
    for k, vs in arr.items():
        if not vs: # 만약 해당 영양소가 전부 비어있으면, 기본값(0~1)으로 채워줌
            q[k] = {"p10":0,"p25":0,"p50":0,"p75":1,"p90":1}
            continue
        vs = np.array(vs, dtype=float)
        q[k] = { # 데이터의 분위수를 뽑는 함수
            "p10": float(np.percentile(vs, 10)), # 하위 10%
            "p25": float(np.percentile(vs, 25)), # 하위 25%
            "p50": float(np.percentile(vs, 50)), # 중앙값
            "p75": float(np.percentile(vs, 75)), # 상위 25%
            "p90": float(np.percentile(vs, 90)), # 상위 10%
        }
    return Calib(q=q)

# 정규화
def _to_z01(x, lo, hi, invert=False):
    if hi <= lo: # 범위 잘못되면 중앙값 리턴
        return 0.5
    v = _clip(x, lo, hi) # lo~hi 구간을 0~1 사이 값으로 매핑
    u = (v - lo) / (hi - lo)
    return (1.0 - u) if invert else u # invert가 True일 경우 높을수록 좋은 값/ False일 경우 낮을수록 좋은 값

# 점수 계산
def compute_score(concept: str, r: dict, calib: Optional[Calib]) -> float:
    name    = str(r.get("name") or "")
    kcal    = _safe(r.get("kcal"))
    protein = _safe(r.get("protein"))
    fat     = _safe(r.get("fat"))
    carbs   = _safe(r.get("carbs"))
    sugar   = _safe(r.get("sugar"))
    fiber   = _safe(r.get("fiber"))
    sodium  = _safe(r.get("sodium"))
    sat     = _safe(r.get("sat_fat", fat))
    netc    = _net_carb(carbs, fiber)

    def q(k, key): # 정규화 기준점
        if calib and calib.q.get(key):
            return calib.q[key][k]
        defaults = {
            "kcal": (50, 600), "protein": (2, 25), "fat": (0.5, 30),
            "carbs": (1, 70), "sugar": (0.5, 20), "fiber": (0.5, 10),
            "sodium": (50, 1200), "sat_fat": (0.1, 10), "netcarb": (1, 60),
        }
        lo, hi = defaults.get(key, (0,1))
        return {"p10":lo, "p90":hi}[k] # 10% 분위값 / 90% 분위값

    z = {}
    z["kcal_low"]   = _to_z01(kcal,  q("p10","kcal"),    q("p90","kcal"),    invert=True)
    z["kcal_high"]  = _to_z01(kcal,  q("p10","kcal"),    q("p90","kcal"))
    z["protein"]    = _to_z01(protein, q("p10","protein"), q("p90","protein"))
    z["fat_low"]    = _to_z01(fat,   q("p10","fat"),     q("p90","fat"),     invert=True)
    z["fat_high"]   = _to_z01(fat,   q("p10","fat"),     q("p90","fat"))
    z["carb_low"]   = _to_z01(carbs, q("p10","carbs"),   q("p90","carbs"),   invert=True)
    z["sugar_low"]  = _to_z01(sugar, q("p10","sugar"),   q("p90","sugar"),   invert=True)
    z["fiber"]      = _to_z01(fiber, q("p10","fiber"),   q("p90","fiber"))
    z["sodium_low"] = _to_z01(sodium,q("p10","sodium"),  q("p90","sodium"),  invert=True)
    z["sat_low"]    = _to_z01(sat,   q("p10","sat_fat"), q("p90","sat_fat"), invert=True)
    z["netcarb_low"]= _to_z01(netc,  q("p10","netcarb"), q("p90","netcarb"), invert=True)

    hard_pen = 0.0 # 강제 페널티/보너스
    if sodium > 2000: hard_pen -= 0.15
    if sugar  >   30: hard_pen -= 0.10
    if kcal   >  800: hard_pen -= 0.10
    if sat    >   15: hard_pen -= 0.08

    if concept == "diet":
        w = dict(
            kcal_low=0.28, protein=0.25, sugar_low=0.12,
            sodium_low=0.10,
            fat_low=0.12, fiber=0.08, netcarb_low=0.05
        )
        if kcal > 150: hard_pen -= 0.15
        if sugar > 4:  hard_pen -= 0.15
        if carbs > 15: hard_pen -= 0.10

        if kcal < 80:   hard_pen += 0.25
        elif kcal < 120: hard_pen += 0.20
        elif kcal < 150: hard_pen += 0.15


    elif concept == "keto":
        w = dict(
            netcarb_low=0.40, fat_high=0.15, protein=0.20,
            sugar_low=0.10, sodium_low=0.10, sat_low=0.05
        )
        if netc > 15:   hard_pen -= 0.20
        if sodium > 800: hard_pen -= 0.08


    elif concept == "low_sodium":
        w = dict(
            sodium_low=0.60,
            kcal_low=0.12,
            sugar_low=0.12,
            protein=0.08,
            fiber=0.06,
            fat_low=0.02
        )
        s = sodium
        if s > 240: return 0.0
        if s > 60:  hard_pen -= min(0.35, 0.0014 * (s - 60))
        if s > 80:  hard_pen -= 0.06
        if s > 120: hard_pen -= 0.18
        if s > 160: hard_pen -= 0.22
        if s > 200: hard_pen -= 0.30
        if name and _SOUP_RE.search(name):
            hard_pen -= 0.08


    elif concept == "glycemic":
        w = dict(
            netcarb_low=0.35, sugar_low=0.20, fiber=0.15,
            protein=0.15, sat_low=0.10, sodium_low=0.10
        )
        if sugar > 2:  hard_pen -= 0.20
        if netc  > 7:  hard_pen -= 0.25
        if sodium > 230: hard_pen -= 0.15
        elif sodium > 180: hard_pen -= 0.08


    elif concept == "bulking":
        prot_dens = _ratio(protein, max(kcal, 1e-9))
        z["prot_density"] = _to_z01(prot_dens, 0.02, 0.25)

        w = dict(
            protein=0.50,
            prot_density=0.15,
            kcal_high=0.15,
            fat_high=0.05,
            sugar_low=0.05,
            sodium_low=0.03,
            sat_low=0.02
        )

        if protein < 6:        hard_pen -= 0.15
        if prot_dens < 0.04:   hard_pen -= 0.15

        if protein > 15:       hard_pen += 0.65
        if protein > 17:       hard_pen += 0.75
        if protein > 20:       hard_pen += 0.85
        if prot_dens > 0.10:   hard_pen += 0.65
        if prot_dens > 0.15:   hard_pen += 0.75
        if prot_dens > 0.20:   hard_pen += 0.85 
        base = sum(z.get(k, 0.0) * wv for k, wv in w.items())
        score = base * (1 + hard_pen)


    else:
        w = dict(
            protein=0.25, fiber=0.10, sugar_low=0.15,
            sodium_low=0.15, fat_low=0.10, netcarb_low=0.25
        )

    base = sum(z.get(k, 0.0) * wv for k, wv in w.items())
    score = base + hard_pen
    return _clip(score, 0.0, 1.0) * 100.0
