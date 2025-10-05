from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

# Import your new master engine function
from engine.master_engine import run_master_pipeline

app = FastAPI(
    title="NASA Knowledge Engine Backend",
    description="Provides on-demand analysis using the master processing pipeline.",
    version="1.0.0"
)

# Pydantic model to validate the incoming request from the Dash app
class AnalysisRequest(BaseModel):
    search_text: str
    live_scrape: bool = False

@app.post("/api/generate-analysis")
def generate_analysis(request: AnalysisRequest):
    """
    This single endpoint drives the entire application.
    It calls the backend model and returns the formatted results.
    """
    try:
        results = run_master_pipeline(
            search_text=request.search_text,
            live_scrape=request.live_scrape
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine Error: {str(e)}")
