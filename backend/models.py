"""
SQLAlchemy models for local PostgreSQL (if not using Supabase).
"""
from sqlalchemy import Column, String, Text, Date, Time, Numeric, Integer, Boolean, ForeignKey, ARRAY, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from database import Base


class TenderType(enum.Enum):
    AOON = "AOON"
    AOOI = "AOOI"


class TenderStatus(enum.Enum):
    SCRAPED = "SCRAPED"
    LISTED = "LISTED"
    ANALYZED = "ANALYZED"
    ERROR = "ERROR"


class DocumentType(enum.Enum):
    AVIS = "AVIS"
    RC = "RC"
    CPS = "CPS"
    ANNEXE = "ANNEXE"
    OTHER = "OTHER"


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_url = Column(Text, nullable=False, unique=True)
    scraped_at = Column(Date, server_default=func.now())
    scrape_date = Column(Date, nullable=False)
    status = Column(Enum(TenderStatus), default=TenderStatus.SCRAPED)
    error_message = Column(Text)
    
    reference_tender = Column(Text)
    tender_type = Column(Enum(TenderType))
    issuing_institution = Column(Text)
    subject = Column(Text)
    total_estimated_value = Column(Numeric(15, 2))
    
    submission_deadline_date = Column(Date)
    submission_deadline_time = Column(Time)
    deadline_source = Column(Text)
    deadline_source_date = Column(Date)
    
    folder_opening_location = Column(Text)
    
    keywords_en = Column(ARRAY(Text), default=[])
    keywords_fr = Column(ARRAY(Text), default=[])
    keywords_ar = Column(ARRAY(Text), default=[])

    # Relationships
    documents = relationship("TenderDocument", back_populates="tender")
    lots = relationship("TenderLot", back_populates="tender")
    analysis = relationship("TenderAnalysis", back_populates="tender")
    chats = relationship("TenderChat", back_populates="tender")


class TenderLot(Base):
    __tablename__ = "tender_lots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    
    lot_number = Column(Integer, nullable=False)
    lot_subject = Column(Text)
    lot_estimated_value = Column(Numeric(15, 2))
    caution_provisoire = Column(Numeric(15, 2))

    tender = relationship("Tender", back_populates="lots")


class TenderDocument(Base):
    __tablename__ = "tender_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    
    document_type = Column(Enum(DocumentType), nullable=False)
    original_filename = Column(Text)
    page_count = Column(Integer)
    extracted_text = Column(Text)
    extraction_method = Column(Text)
    source_date = Column(Date)
    is_annex_override = Column(Boolean, default=False)

    tender = relationship("Tender", back_populates="documents")


class TenderAnalysis(Base):
    __tablename__ = "tender_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    
    analysis_data = Column(JSON, default={})
    model_used = Column(Text)
    tokens_used = Column(Integer)
    analysis_cost = Column(Numeric(10, 6))

    tender = relationship("Tender", back_populates="analysis")


class TenderChat(Base):
    __tablename__ = "tender_chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text)
    detected_language = Column(Text)

    tender = relationship("Tender", back_populates="chats")
