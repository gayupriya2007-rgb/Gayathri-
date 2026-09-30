import os
from pathlib import Path

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

router = APIRouter()

app = FastAPI(
    title="LegalEase API",
    version="1.0.0",
)

# Load .env from backend/frontend/.env
env_file = Path(__file__).parent / "frontend" / ".env"
load_dotenv(env_file)


class DocumentRequest(BaseModel):
    document_type: str
    parties: str
    terms: str
    effective_date: str


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/generate")
def generate_document(request: DocumentRequest):
    """
    Generate a basic legal document.
    Gemini will be used when a valid API key is available.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    prompt = f"""
Create a professional legal document.

Document Type: {request.document_type}
Parties: {request.parties}
Effective Date: {request.effective_date}
Terms and Conditions:
{request.terms}

Write a clear, professional draft with:
1. Title
2. Parties
3. Effective Date
4. Scope / Purpose
5. Terms and Conditions
6. Confidentiality
7. Intellectual Property
8. Termination
9. Governing Law
10. Signatures

This is a general informational draft and not legal advice.
"""

    # Try Gemini
    if api_key and api_key != "your_gemini_api_key_here":
        try:
            from google import genai

            client = genai.Client(api_key=api_key)

            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            document = response.text

            return {
                "status": "success",
                "document": document
            }

        except Exception as e:
            print("Gemini error:", e)

    # Fallback document if Gemini is unavailable
    document = f"""
{request.document_type.upper()}

This Agreement is effective as of {request.effective_date}.

PARTIES

{request.parties}

PURPOSE

This document establishes the terms and conditions agreed upon by the parties.

TERMS AND CONDITIONS

{request.terms}

CONFIDENTIALITY

The parties agree to maintain the confidentiality of information shared
during the course of this agreement.

INTELLECTUAL PROPERTY

Any intellectual property rights shall be handled according to the
terms agreed upon by the parties.

TERMINATION

Either party may terminate this agreement according to the applicable
terms and conditions agreed upon by the parties.

GOVERNING LAW

This agreement shall be governed by the applicable laws agreed upon
by the parties.

SIGNATURES

Party 1: __________________________

Party 2: __________________________

Date: _____________________________

Note: This is an AI-assisted general informational draft and is not legal advice.
"""

    return {
        "status": "success",
        "document": document
    }


app.include_router(router)