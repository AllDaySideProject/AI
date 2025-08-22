from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from contextlib import asynccontextmanager

from app.domain.recommend.service import loader
from app.domain.tip.api import tip_api
from app.domain.recommend.api import recommend_api
from app.core.exception.global_error_handler import (
    validation_error_handler,
    http_exception_handler,
    global_exception_handler,
)

import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, loader.load_all)  
    loader.load_all()
    print("모델/DB 로딩 완료")

    yield # 여기까지 오면 서버 실행

app = FastAPI(
    title="LeftOversFlirting AI",
    lifespan=lifespan
)

# 라우터 등록
app.include_router(tip_api.router)
app.include_router(recommend_api.router)

@app.get("/healthz")
def healthz():
    return {"ok": True}


# 전역 핸들러 등록
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
