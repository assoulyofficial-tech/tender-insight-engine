"""
Tender CRUD endpoints.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database import get_db, supabase
from models import Tender
from schemas import TenderResponse, TenderCreate

router = APIRouter()


@router.get("/", response_model=List[TenderResponse])
async def list_tenders(
    search: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """List tenders with optional filtering."""
    if supabase:
        # Use Supabase REST API
        query_parts = []
        if search:
            query_parts.append(f"or=(subject.ilike.*{search}*,issuing_institution.ilike.*{search}*)")
        if status:
            query_parts.append(f"status=eq.{status}")
        query_parts.append(f"limit={limit}")
        query_parts.append(f"offset={offset}")
        query_parts.append("order=scrape_date.desc")
        
        return await supabase.select("tenders", "&".join(query_parts))
    else:
        # Use SQLAlchemy
        query = db.query(Tender)
        if search:
            query = query.filter(
                Tender.subject.ilike(f"%{search}%") |
                Tender.issuing_institution.ilike(f"%{search}%")
            )
        if status:
            query = query.filter(Tender.status == status)
        return query.order_by(Tender.scrape_date.desc()).offset(offset).limit(limit).all()


@router.get("/{tender_id}", response_model=TenderResponse)
async def get_tender(tender_id: str, db: Session = Depends(get_db)):
    """Get a single tender by ID."""
    if supabase:
        result = await supabase.select("tenders", f"id=eq.{tender_id}")
        if not result:
            raise HTTPException(status_code=404, detail="Tender not found")
        return result[0]
    else:
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise HTTPException(status_code=404, detail="Tender not found")
        return tender


@router.get("/{tender_id}/documents")
async def get_tender_documents(tender_id: str, db: Session = Depends(get_db)):
    """Get documents for a tender."""
    if supabase:
        return await supabase.select("tender_documents", f"tender_id=eq.{tender_id}")
    else:
        # TODO: SQLAlchemy implementation
        return []


@router.get("/{tender_id}/lots")
async def get_tender_lots(tender_id: str, db: Session = Depends(get_db)):
    """Get lots for a tender."""
    if supabase:
        return await supabase.select("tender_lots", f"tender_id=eq.{tender_id}&order=lot_number")
    else:
        # TODO: SQLAlchemy implementation
        return []
