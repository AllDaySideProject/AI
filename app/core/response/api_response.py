from typing import Generic, Optional, TypeVar
from pydantic.generics import GenericModel
from datetime import datetime, timezone

T = TypeVar("T")

# API 응답을 감싸는 공통 래퍼 dto
class Envelope(GenericModel, Generic[T]):
    isSuccess: bool
    httpStatus: int
    data: Optional[T] = None
    timeStamp: str

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# 성공 응답을 Envelope 형태로 감싸서 반환
def ok(data: T, http_status: int = 200) -> Envelope[T]:
    return Envelope[T](
        isSuccess=True,
        httpStatus=http_status,
        data=data,
        timeStamp=now_iso(),
    )

# 실패 응답을 Envelope 형태로 감싸서 반환
def fail(http_status: int, data: Optional[dict] = None) -> Envelope[dict]:
    return Envelope[dict](
        isSuccess=False,
        httpStatus=http_status,
        data=data or {},
        timeStamp=now_iso(),
    )