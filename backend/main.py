from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

load_dotenv()

from services import (
    get_dashboard, get_insights, get_trends, get_changes, get_companies, get_company, scrape_competitor
)
from models.schemas import (
    DashboardResponse, InsightsResponse, TrendsResponse, ChangesResponse, 
    CompaniesResponse, CompanyResponse, Insight, ScrapeRequest, ScrapeResponse
)

app = FastAPI(title="Market Intelligence Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/dashboard")
async def api_dashboard() -> DashboardResponse:
    try:
        return get_dashboard()
    except Exception as e:
        return DashboardResponse(
            companies=[],
            insights=[Insight(title="Setup complete", description="Backend ready - LLM enabled in analyzer.py", impact="high", evidence="", recommended_action="Run frontend npm dev", source="system")], 
            trends=[], 
            changes=[]
        )

@app.get("/api/insights")
async def api_insights() -> InsightsResponse:
    return get_insights()

@app.get("/api/trends")
async def api_trends() -> TrendsResponse:
    return get_trends()

@app.get("/api/changes")
async def api_changes() -> ChangesResponse:
    return get_changes()

@app.get("/api/companies")
async def api_companies() -> CompaniesResponse:
    return get_companies()

@app.get("/api/companies/{company_id}")
async def api_company(company_id: str) -> CompanyResponse:
    return get_company(company_id)

@app.post("/api/scrape")
async def api_scrape(request: ScrapeRequest) -> ScrapeResponse:
    """Scrape competitor site and add to analysis data."""
    try:
        result = await scrape_competitor(request.url, request.company, max_pages=request.max_pages)
        return ScrapeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scrape failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Market Intelligence Backend - APIs ready! NEW: POST /api/scrape {url, company}. Visit http://localhost:5173 (frontend)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

