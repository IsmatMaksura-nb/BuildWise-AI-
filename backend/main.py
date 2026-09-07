from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

from backend.agents.construction_agent import agent


# ============================================================
# 1. FASTAPI APP
# ============================================================

app = FastAPI(
    title="BuildWise-AI Backend",
    description="AI-powered construction assistant backend",
    version="1.0.0"
)


# ============================================================
# 2. CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 3. REQUEST MODELS
# ============================================================

class ChatRequest(BaseModel):
    message: str
    feature: str = "general"
    language: str = "English"


class CostRequest(BaseModel):
    building_type: str = "Residential"
    area_sqft: float = 1500
    floors: int = 1
    quality: str = "Standard"
    notes: str = ""
    language: str = "English"


class MarketRequest(BaseModel):
    query: str
    language: str = "English"


# ============================================================
# 4. ROOT ENDPOINT
# ============================================================

@app.get("/")
def read_root():
    return {
        "message": "BuildWise-AI Backend is running!",
        "status": "success",
        "version": "1.0"
    }


# ============================================================
# 5. HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "BuildWise-AI Backend"
    }


# ============================================================
# 6. GENERAL CHAT
# ============================================================

@app.post("/api/chat")
def chat(request: ChatRequest):

    try:
        response = agent.process_query(
            feature=request.feature,
            user_input=request.message,
            language=request.language
        )

        # --------------------------------------------------------
        # Fix malformed Markdown table headers
        # --------------------------------------------------------
        response = re.sub(
            r"\|\s*#\s*Purpose\s*Engineering Rationale\s*\|\s*\|\s*\|",
            "| # | Purpose | Engineering Rationale |",
            response,
            flags=re.IGNORECASE
        )

        return {
            "success": True,
            "feature": request.feature,
            "response": response
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# 7. DOCUMENT ANALYZER
# ============================================================

@app.post("/api/analyze-doc")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form("Analyze this construction document."),
    language: str = Form("English")
):

    try:

        # Read uploaded document
        file_bytes = await file.read()

        # Validate file
        if not file_bytes:
            return {
                "success": False,
                "error": "Uploaded document is empty."
            }

        # Send document to Construction Agent
        response = agent.process_query(
            feature="doc",
            user_input=query,
            file_bytes=file_bytes,
            file_name=file.filename,
            language=language
        )

        return {
            "success": True,
            "file_name": file.filename,
            "response": response
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# 8. VISUAL INSPECTOR
# ============================================================

@app.post("/api/inspect-image")
async def inspect_image(
    file: UploadFile = File(...),
    query: str = Form("Inspect this construction image."),
    language: str = Form("English")
):

    try:

        file_bytes = await file.read()

        if not file_bytes:
            return {
                "success": False,
                "error": "Uploaded image is empty."
            }

        response = agent.process_query(
            feature="visual",
            user_input=query,
            file_bytes=file_bytes,
            file_name=file.filename,
            language=language
        )

        return {
            "success": True,
            "file_name": file.filename,
            "response": response
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# 9. COST ESTIMATOR
# ============================================================

@app.post("/api/estimate-cost")
def estimate_cost(request: CostRequest):

    try:

        response = agent.process_query(
            feature="cost",
            user_input=request.notes,
            language=request.language,
            extra_data={
                "building_type": request.building_type,
                "area_sqft": request.area_sqft,
                "floors": request.floors,
                "quality": request.quality,
                "notes": request.notes
            }
        )

        return {
            "success": True,
            "response": response
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# 10. MARKET SEARCH
# ============================================================

@app.post("/api/market-search")
def market_search(request: MarketRequest):

    try:

        print("\n🔥 MARKET API CALLED")
        print(f"🔥 MARKET QUERY: {request.query}")
        print(f"🔥 MARKET LANGUAGE: {request.language}")

        response = agent.process_query(
            feature="market",
            user_input=request.query,
            language=request.language
        )

        print("🔥 MARKET RESPONSE GENERATED")

        return {
            "success": True,
            "query": request.query,
            "response": response
        }

    except Exception as e:

        print(f"🔥 MARKET API ERROR: {e}")

        return {
            "success": False,
            "error": str(e)
        }