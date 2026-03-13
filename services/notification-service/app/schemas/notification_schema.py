from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class NotificationSendRequest(BaseModel):
    email: EmailStr
    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1)
    correlation_id: Optional[str] = Field(None, max_length=100)


class NotificationSendResponse(BaseModel):
    notification_id: int
    status: str


class NotificationStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    subject: str
    body: str
    status: str
    correlation_id: Optional[str] = None
    sendgrid_message_id: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
