"""
AI Analyzer Service.
Uses DeepSeek API for tender analysis.
"""
import json
from typing import Optional
from openai import AsyncOpenAI

from config import settings
from database import supabase

# Avis metadata extraction schema
AVIS_SCHEMA = {
    "reference_tender": "",
    "tender_type": "AOON | AOOI",
    "issuing_institution": "",
    "submission_deadline": {"date": "", "time": ""},
    "folder_opening_location": "",
    "subject": "",
    "total_estimated_value": "",
    "keywords": {
        "keywords_eng": [],
        "keywords_fr": [],
        "keywords_ar": [],
    },
    "lots": [
        {
            "lot_number": "",
            "lot_subject": "",
            "lot_estimated_value": "",
            "caution_provisoire": "",
        }
    ],
}

AVIS_EXTRACTION_PROMPT = """You are an expert at extracting structured data from Moroccan government tender documents.

Extract the following information from the AVIS document text. Return a valid JSON object matching this schema:

{schema}

Rules:
1. Extract exactly 10 keywords per language (English, French, Arabic)
2. Keywords should be relevant for searching this tender
3. If a field is not found, leave it as empty string or empty array
4. For tender_type, use "AOON" for "Appel d'Offres Ouvert National" or "AOOI" for international
5. Parse dates in DD/MM/YYYY format
6. Parse monetary values as numbers (remove MAD suffix)

AVIS Document Text:
{text}

Return ONLY the JSON object, no markdown or explanation."""

ASK_AI_PROMPT = """You are an expert assistant on Moroccan government tenders.

You have access to the following tender documents:
{context}

Answer the user's question about this tender. Be precise and cite specific sections when possible.
Support French and Moroccan Darija (Arabic dialect) questions.

User Question: {question}

Provide a clear, expert answer:"""


class AIAnalyzer:
    """AI-powered tender analysis using DeepSeek."""

    def __init__(self):
        if settings.DEEPSEEK_API_KEY:
            self.client = AsyncOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_API_BASE,
            )
        else:
            self.client = None

    async def extract_avis_metadata(self, tender_id: str) -> dict:
        """Extract metadata from AVIS document using AI."""
        if not self.client:
            raise Exception("DeepSeek API not configured")

        # Get AVIS document
        docs = await supabase.select(
            "tender_documents",
            f"tender_id=eq.{tender_id}&document_type=eq.AVIS"
        )

        if not docs:
            # Fallback to RC
            docs = await supabase.select(
                "tender_documents",
                f"tender_id=eq.{tender_id}&document_type=eq.RC"
            )

        if not docs or not docs[0].get("extracted_text"):
            raise Exception("No AVIS or RC document found")

        avis_text = docs[0]["extracted_text"]

        # Call DeepSeek
        prompt = AVIS_EXTRACTION_PROMPT.format(
            schema=json.dumps(AVIS_SCHEMA, indent=2),
            text=avis_text[:15000],  # Limit context
        )

        response = await self.client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        result_text = response.choices[0].message.content

        # Parse JSON
        try:
            # Clean markdown if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]

            metadata = json.loads(result_text)
        except json.JSONDecodeError:
            metadata = {"error": "Failed to parse AI response", "raw": result_text}

        # Update tender with extracted metadata
        update_data = {}
        if metadata.get("reference_tender"):
            update_data["reference_tender"] = metadata["reference_tender"]
        if metadata.get("tender_type"):
            update_data["tender_type"] = metadata["tender_type"]
        if metadata.get("issuing_institution"):
            update_data["issuing_institution"] = metadata["issuing_institution"]
        if metadata.get("subject"):
            update_data["subject"] = metadata["subject"]
        if metadata.get("keywords", {}).get("keywords_eng"):
            update_data["keywords_en"] = metadata["keywords"]["keywords_eng"]
        if metadata.get("keywords", {}).get("keywords_fr"):
            update_data["keywords_fr"] = metadata["keywords"]["keywords_fr"]
        if metadata.get("keywords", {}).get("keywords_ar"):
            update_data["keywords_ar"] = metadata["keywords"]["keywords_ar"]

        update_data["status"] = "LISTED"

        if update_data:
            await supabase.update("tenders", f"id=eq.{tender_id}", update_data)

        # Insert lots
        for lot in metadata.get("lots", []):
            if lot.get("lot_number"):
                await supabase.insert("tender_lots", {
                    "tender_id": tender_id,
                    "lot_number": int(lot["lot_number"]) if lot["lot_number"] else 0,
                    "lot_subject": lot.get("lot_subject"),
                    "lot_estimated_value": float(lot["lot_estimated_value"]) if lot.get("lot_estimated_value") else None,
                    "caution_provisoire": float(lot["caution_provisoire"]) if lot.get("caution_provisoire") else None,
                })

        return metadata

    async def deep_analysis(self, tender_id: str) -> dict:
        """Perform deep analysis on tender documents."""
        if not self.client:
            raise Exception("DeepSeek API not configured")

        # Get all documents
        docs = await supabase.select(
            "tender_documents",
            f"tender_id=eq.{tender_id}"
        )

        if not docs:
            raise Exception("No documents found")

        # Combine all text
        all_text = "\n\n---\n\n".join([
            f"[{d['document_type']}]\n{d['extracted_text'][:5000]}"
            for d in docs if d.get("extracted_text")
        ])

        # TODO: Add universal field extraction prompt
        # For now, return document summary
        response = await self.client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[{
                "role": "user",
                "content": f"Analyze this tender and provide a structured summary:\n\n{all_text[:20000]}"
            }],
            temperature=0.2,
        )

        analysis = {
            "summary": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens if response.usage else 0,
        }

        # Store analysis
        await supabase.insert("tender_analysis", {
            "tender_id": tender_id,
            "analysis_data": analysis,
            "model_used": settings.DEEPSEEK_MODEL,
            "tokens_used": analysis.get("tokens_used", 0),
        })

        # Update status
        await supabase.update("tenders", f"id=eq.{tender_id}", {"status": "ANALYZED"})

        return analysis

    async def ask_question(self, tender_id: str, question: str) -> dict:
        """Answer a question about a tender."""
        if not self.client:
            raise Exception("DeepSeek API not configured")

        # Detect language (simple heuristic)
        language = "fr"
        if any(ord(c) > 1500 for c in question):  # Arabic characters
            language = "ar"

        # Get all documents
        docs = await supabase.select(
            "tender_documents",
            f"tender_id=eq.{tender_id}"
        )

        context = "\n\n".join([
            f"=== {d['document_type']} ===\n{d['extracted_text'][:3000]}"
            for d in docs if d.get("extracted_text")
        ])

        prompt = ASK_AI_PROMPT.format(context=context[:20000], question=question)

        response = await self.client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return {
            "answer": response.choices[0].message.content,
            "language": language,
            "tokens_used": response.usage.total_tokens if response.usage else 0,
        }
