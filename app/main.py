# FastAPI 앱 객체 생성하고, api/predict.py 라우트를 include
from fastapi import FastAPI
from app.api import tip

app = FastAPI(title="LeftOversFlirting AI")
app.include_router(tip.router)
