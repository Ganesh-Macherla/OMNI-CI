from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ImpactLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Insight(BaseModel):
    title: str
    description: str
    impact: ImpactLevel
    evidence: str
    recommended_action: str
    source: str

class Trend(BaseModel):
    title: str
    description: str
    type: str  # "pricing", "messaging", "feature"
    source: str

class Change(BaseModel):
    title: str
    description: str
    type: str  # "added", "removed", "updated"
    date_detected: Optional[str] = None
    source: str

class Company(BaseModel):
    id: str
    name: str
    website: Optional[str] = None
    overview: Optional[str] = None
    dossier: Optional[str] = None

class DashboardResponse(BaseModel):
    companies: List[Company]
    insights: List[Insight]
    trends: List[Trend]
    changes: List[Change]
    timestamp: str = "2024"

class CompaniesResponse(BaseModel):
    companies: List[Company]

class CompanyResponse(BaseModel):
    company: Company

class InsightsResponse(BaseModel):
    insights: List[Insight]

class TrendsResponse(BaseModel):
    trends: List[Trend]

class ChangesResponse(BaseModel):
    changes: List[Change]

class ScrapeRequest(BaseModel):
    url: str
    company: str
    max_pages: Optional[int] = 30

class ScrapeResponse(BaseModel):
    status: str
    company: str
    files_saved: int
    total_pages: int
    output_dir: str

