from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# ---------- Auth ----------

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime
    class Config:
        from_attributes = True


# ---------- Chat ----------

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class ToolCallOut(BaseModel):
    id: str
    name: str
    args: dict

class ApprovalOut(BaseModel):
    id: str
    tool_call_id: str
    tool_name: str
    tool_args: dict
    status: str
    class Config:
        from_attributes = True

class MessageOut(BaseModel):
    id: str
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[dict]] = None
    tool_call_id: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    conversation_id: str
    message: MessageOut
    approval: Optional[ApprovalOut] = None

class ConversationOut(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True
