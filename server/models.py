from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: str
    upload_time: datetime
    status: str
    raw_text: Optional[str] = None
    document_kind: Optional[str] = None


class ExtractedFieldOut(BaseModel):
    id: int
    document_id: int
    field_name: str
    field_category: str
    extracted_value: Optional[str] = None
    reviewed_value: Optional[str] = None
    confidence: str
    is_approved: bool


class FieldUpdate(BaseModel):
    reviewed_value: Optional[str] = None
    is_approved: Optional[bool] = None


class BulkApprove(BaseModel):
    field_ids: list[int]


class BulkApproveDocs(BaseModel):
    document_ids: list[int]
