from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class AskRequest(BaseModel):
    question: str
    show_sql: bool = False
    session_id: Optional[str] = None

class Message(BaseModel):
    role: str
    text: str

class AskResponse(BaseModel):
    session_id: str
    reply_text: str
    final_sql: Optional[str] = None
    rows: List[Dict[str, Any]] = []
    rowcount: int = 0
    messages: List[Message] = []