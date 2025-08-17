# FastAPI 앱 객체 생성하고, api/predict.py 라우트를 include
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.core.ApiResponse import Envelope,fail

app = FastAPI(title="LeftOversFlirting AI")

from app.api import tip
app.include_router(tip.router)

# HTTPException 공통 래핑
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(exc.status_code, {"message": exc.detail}).model_dump(),
    )

# 기타 모든 예외 공통 래핑
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=fail(500, {"message": "Fast API 서버 내 오류가 발생했습니다."}).model_dump(),
    )