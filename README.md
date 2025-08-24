# 🤖 잔반플러팅 AI

FastAPI 기반의 **AI 추천 서버**로, 식약처 영양성분표 데이터를 기반으로
**맞춤형 반찬 추천**과 **섭취 팁 제공**을 담당합니다.

### 🔹 AI 기능

* **메뉴 추천**

  * 5가지 콘셉트 기반:
    `diet(다이어트)`, `keto(저탄고지)`, `low_sodium(저염)`, `glycemic(혈당)`, `bulking(벌크업)`
  * 입력 메뉴명 -> 유사도 매칭 -> 영양 성분 피처화 -> 콘셉트별 점수화(0\~100)

* **Tip 생성**

  * OpenAI API 연동을 통한 **식습관 가이드 / 레시피 제안**

---

## 🚀 Tech Stack

### 🔹 Framework & Language
- **Python 3.11**
- **FastAPI : 경량 웹 프레임워크**
- **Uvicorn : ASGI 서버**

<img src="https://img.shields.io/badge/Python%203.11-3776AB?style=flat-square&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/> <img src="https://img.shields.io/badge/Uvicorn-499848?style=flat-square&logo=python&logoColor=white"/>



### 🔹 Data / ML
- **scikit-learn : 벡터화, 차원 축소, 스케일링, 결측치 보정**
- **hnswlib : 근접 탐색 (메뉴명 유사도 매칭)**
- **numpy / joblib : 수치 연산 및 모델 직렬화**
-**식약처 영양성분표 데이터 (Excel/CSV) : 영양 정보 기반 학습/추천**
  
<img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white"/> <img src="https://img.shields.io/badge/hnswlib-333333?style=flat-square&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/numpy-013243?style=flat-square&logo=numpy&logoColor=white"/> <img src="https://img.shields.io/badge/joblib-333333?style=flat-square&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/%EC%8B%9D%EC%95%BD%EC%B2%98%20%EC%98%81%EC%96%91%EC%84%B1%EB%B6%84%ED%91%9C-0052CC?style=flat-square&logo=google-spreadsheet&logoColor=white"/>


---

## 📂 Project Structure

```text
📦 menu-ai
├── Dockerfile
├── main.py                # FastAPI 실행 엔트리포인트
├── requirements.txt
├── leftovers
│   ├── core                # 설정, 에러 핸들러, 공통 응답, 외부 클라이언트
│   └── domain
│       ├── recommend       # 메뉴 추천 도메인
│       │   ├── api/        # 추천 API
│       │   ├── data/       # 원본 영양 데이터 (식약처 엑셀)
│       │   ├── model_store # 학습된 모델 및 전처리 아티팩트
│       │   ├── schemas/    # 요청/응답 스키마
│       │   └── service/    # 추천 로직 (매칭, 스코어링, 전처리, 학습)
│       └── tip             # 팁/레시피 도메인
│           ├── api/        # Tip API
│           ├── schemas/    # 요청/응답 스키마
│           └── service/    # 프롬프트/LLM 호출
```

---

## 🔬 데이터 파이프라인 & 알고리즘

1. **데이터 로딩**

   * 식약처 영양 데이터(`.xlsx`) 로드 -> 결측치 보정(Imputer) -> 정규화(Scaler)

2. **메뉴명 매칭**

   * TF-IDF 벡터화 -> TruncatedSVD 차원 축소 -> hnswlib 근접 탐색으로 유사 메뉴 검색

3. **영양 피처화**

   * `kcal, protein, fat, carbs, sugar, sodium` 등 주요 영양소를 벡터화

4. **스코어링 (Concept Scoring)**

   * 다이어트: 열량·당류·탄수화물 제한
   * 저염: 나트륨 엄격 제한
   * 혈당: 당류·탄수화물 동시 제한
   * 저탄고지/벌크업: 기존 비율 유지

5. **추천 결과 반환**

   * 점수(0\~100) 기반 랭킹 → 상위 N개 반환
   * 응답 구조: `isSuccess`, `httpStatus`, `data`, `timeStamp`

---

## ⚙️ 실행 방법

### 1. 의존성 설치

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --no-cache-dir -r requirements.txt
```

### 2. 학습 (모델 생성)

최초 실행 시, `model_store/`가 비어 있다면 학습 과정이 필요합니다.

```bash
python -m leftovers.domain.recommend.service.train
```

→ `nutrition_imputer.joblib`, `nutrition_scaler.joblib`, `concept_model_*.joblib` 등이 생성됩니다.

### 3. 서버 실행

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
