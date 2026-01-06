"""
AI Analysis endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db, supabase
from services.ai_analyzer import AIAnalyzer
from config import settings

router = APIRouter()


class AnalyzeRequest(BaseModel):
    tender_id: str


class AskRequest(BaseModel):
    tender_id: str
    question: str


@router.post("/avis")
async def analyze_avis(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    AI Pipeline 1: Extract Avis metadata.
    Triggered automatically after document extraction.
    """
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=503, detail="DeepSeek API key not configured")
    
    analyzer = AIAnalyzer()
    result = await analyzer.extract_avis_metadata(request.tender_id)
    
    return {"status": "success", "data": result}


@router.post("/deep")
async def deep_analysis(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    AI Pipeline 2: Deep analysis.
    Triggered on click (user opens tender details).
    """
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=503, detail="DeepSeek API key not configured")
    
    analyzer = AIAnalyzer()
    result = await analyzer.deep_analysis(request.tender_id)
    
    return {"status": "success", "data": result}


@router.post("/ask")
async def ask_ai(request: AskRequest, db: Session = Depends(get_db)):
    """
    AI Pipeline 3: Ask AI.
    Accept French and Moroccan Darija questions.
    """
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=503, detail="DeepSeek API key not configured")
    
    analyzer = AIAnalyzer()
    response = await analyzer.ask_question(request.tender_id, request.question)
    
    # Store in chat history
    if supabase:
        await supabase.insert("tender_chats", {
            "tender_id": request.tender_id,
            "user_message": request.question,
            "ai_response": response["answer"],
            "detected_language": response.get("language"),
        })
    
    return {"status": "success", "data": response}


@router.get("/chats/{tender_id}")
async def get_chat_history(tender_id: str):
    """Get chat history for a tender."""
    if supabase:
        return await supabase.select(
            "tender_chats",
            f"tender_id=eq.{tender_id}&order=created_at.asc"
        )
    return []
