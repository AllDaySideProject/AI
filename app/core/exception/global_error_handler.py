from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.response.api_response import fail

# 공통 응답 포맷 생성기
def error_response(status: int, message: str, extra: dict = None):
    return JSONResponse(
        status_code=status,
        content=fail(status, {"message": message, **(extra or {})}).model_dump()
    )

# validation 에러
async def validation_error_handler(request: Request, exc: ValidationError):
    return error_response(422, "입력값이 잘못되었습니다.", {"errors": exc.errors()})

# 400/401/403/404 등 비즈니스 로직 조건이 안 맞을 때 발생
async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(exc.status_code, str(exc.detail))

# 나머지 모든 예외
async def global_exception_handler(request: Request, exc: Exception):
    return error_response(500, "서버 내부 오류가 발생했습니다.")
