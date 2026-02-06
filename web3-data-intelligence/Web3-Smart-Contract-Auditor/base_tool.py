from pydantic import BaseModel
from typing import Optional, Any

class ToolResult(BaseModel):
    output: str
    system: Optional[str] = None
    artifact: Optional[Any] = None

class BaseTool(BaseModel):
    name: str = ""
    description: str = ""
    parameters: dict = {}
    
    async def execute(self, **kwargs) -> ToolResult:
        raise NotImplementedError
