"""
Pydantic schemas for API validation.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time
from uuid import UUID


class TenderBase(BaseModel):
    reference_url: str
    scrape_date: date


class TenderCreate(TenderBase):
    pass


class TenderResponse(TenderBase):
    id: UUID
    status: str
    reference_tender: Optional[str] = None
    tender_type: Optional[str] = None
    issuing_institution: Optional[str] = None
    subject: Optional[str] = None
    total_estimated_value: Optional[float] = None
    submission_deadline_date: Optional[date] = None
    submission_deadline_time: Optional[time] = None
    keywords_en: List[str] = []
    keywords_fr: List[str] = []
    keywords_ar: List[str] = []

    class Config:
        from_attributes = True


class TenderLotResponse(BaseModel):
    id: UUID
    tender_id: UUID
    lot_number: int
    lot_subject: Optional[str] = None
    lot_estimated_value: Optional[float] = None
    caution_provisoire: Optional[float] = None

    class Config:
        from_attributes = True


class TenderDocumentResponse(BaseModel):
    id: UUID
    tender_id: UUID
    document_type: str
    original_filename: Optional[str] = None
    page_count: Optional[int] = None
    extraction_method: Optional[str] = None

    class Config:
        from_attributes = True
