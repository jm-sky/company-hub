from pydantic import BaseModel
from typing import Any, Optional

class ApiResponse(BaseModel):
    data: Any
    message: Optional[str] = None
    success: bool
