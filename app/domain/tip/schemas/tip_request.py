from pydantic import BaseModel
from typing import List

class TipRequest(BaseModel):
    menus: List[str]