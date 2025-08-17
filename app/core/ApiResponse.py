from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel
from datetime import datetime, timezone

T = TypeVar("T")

class Envelope(GenericModel, Generic[T]):
    isSuccess: bool
    httpStatus: int
    data: Optional[T] = None
    timeStamp: str

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# 성공 응답
def ok(data: T, http_status: int = 200) -> Envelope[T]:
    return Envelope[T](
        isSuccess=True,
        httpStatus=http_status,
        data=data,
        timeStamp=now_iso(),
    )

# 실패 응답
def fail(http_status: int, data: Optional[dict] = None) -> Envelope[dict]:
    return Envelope[dict](
        isSuccess=False,
        httpStatus=http_status,
        data=data or {},
        timeStamp=now_iso(),
    )