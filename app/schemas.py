from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class Recipient(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("name must contain at least 2 non-whitespace characters")
        return value

class GenerationRequest(BaseModel):
    event_name: str = Field(min_length=2, max_length=200)
    course: str = Field(min_length=2, max_length=200)
    issue_date: date
    recipients: list[Recipient] = Field(min_length=1, max_length=5000)

class GenerationJobResponse(BaseModel):
    job_id: str
    status: Literal["queued", "processing", "completed", "completed_with_errors", "failed"]
    total: int
    processed: int
    successful: int
    failed: int
    errors: list[dict]

class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    job_id: str
    recipient_name: str
    recipient_email: EmailStr
    course: str
    issue_date: date
    status: str
    error_message: str | None
    created_at: datetime
