from pydantic import BaseModel

class TipItem(BaseModel):
    title: str
    content: str