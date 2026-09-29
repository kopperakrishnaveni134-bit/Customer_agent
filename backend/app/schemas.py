from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# =========================
# CUSTOMER
# =========================

class CustomerCreate(BaseModel):
    name: str
    email: str
    plan: str = "Free"


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    plan: str
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# TICKET
# =========================

class TicketCreate(BaseModel):
    customer_id: int
    subject: str
    description: str
    issue_type: Optional[str] = None
    known_issue: Optional[str] = None


class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    customer_id: int
    subject: str
    description: str
    status: str
    issue_type: Optional[str]
    known_issue: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


# =========================
# ENVIRONMENT
# =========================

class EnvironmentCreate(BaseModel):
    customer_id: int
    operating_system: Optional[str] = None
    browser: Optional[str] = None
    device: Optional[str] = None
    app_version: Optional[str] = None
    customer_plan: Optional[str] = None


class EnvironmentResponse(BaseModel):
    id: int
    customer_id: int
    operating_system: Optional[str]
    browser: Optional[str]
    device: Optional[str]
    app_version: Optional[str]
    customer_plan: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


# =========================
# MESSAGE
# =========================

class MessageCreate(BaseModel):
    ticket_id: int
    sender: str
    content: str


class MessageResponse(BaseModel):
    id: int
    ticket_id: int
    sender: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# TROUBLESHOOTING
# =========================

class TroubleshootingCreate(BaseModel):
    ticket_id: int
    solution: str
    result: str
    notes: Optional[str] = None


class TroubleshootingResponse(BaseModel):
    id: int
    ticket_id: int
    solution: str
    result: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# FRUSTRATION
# =========================

class FrustrationCreate(BaseModel):
    customer_id: int
    ticket_id: Optional[int] = None
    level: str
    score: Optional[float] = None
    reason: Optional[str] = None


class FrustrationResponse(BaseModel):
    id: int
    customer_id: int
    ticket_id: Optional[int]
    level: str
    score: Optional[float]
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True