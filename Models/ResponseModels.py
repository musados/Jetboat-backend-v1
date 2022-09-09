from pydantic import BaseModel
from typing import Any, List, Optional

class BasicResponse(BaseModel):
    success: bool
    message: Optional[str] = ''
    data: Any