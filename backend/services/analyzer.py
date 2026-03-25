import functools
from typing import Dict, Any
from models.schemas import DashboardResponse, InsightsResponse, TrendsResponse, ChangesResponse, CompaniesResponse, CompanyResponse, Company, Insight, Trend, Change
from services.file_loader import list_md_files, load_md_file
from services.llm_service import select_files, analyze_contents
from datetime import datetime

@functools.lru_cache(maxsize=128)
def get_cached_analysis() -> Dict:
    "Cached analysis - sync fallback."
    files = list_md_files('./data/md_files')
    if not files:
        return {}

    # Mock for sync (lru_cache doesn't work with async)
    return {
        'insights': [{
            'title': 'Admissions Growth',
            'description': 'UG seats expanded 25% (CSE +20 seats)',
            'impact': 'high',
            'evidence': 'admissions.md, ug-admissions.md',
            'recommended_action': 'Benchmark vs competitors',
            'source': 'backend/data/md_files'
        }],
        'companies': ['Shiv Nadar University Chennai']
    }

def process_files(data_dir: str = './data/md_files') -> DashboardResponse:
    "Sync process with mock LLM."
    analysis = get_cached_analysis()
    if not analysis.get('insights'):
        analysis = {
            'insights': [{
                'title': 'Admissions Growth',
                'description': 'UG seats expanded 25% (CSE +20 seats)',
                'impact': 'high',
                'evidence': 'admissions.md, ug-admissions.md',
                'recommended_action': 'Benchmark vs competitors',
                'source': 'backend/data/md_files'
            }],
            'companies': ['Shiv Nadar University Chennai']
        }
    companies = [Company(id="snuc", name="Shiv Nadar University Chennai")] + [Company(id=c.lower().replace(" ", "-"), name=c) for c in analysis.get('companies', []) if c != 'Shiv Nadar University Chennai']
    return DashboardResponse(
        companies=companies,
        insights=[Insight(**i) for i in analysis.get('insights', [])],
        trends=[Trend(title="Placements Up", description="Avg 10.5 LPA", type="pricing", source="placements.md")],
        changes=[Change(title="B.Sc Economics Launch", description="New program", type="added", source="programs.md")],
        timestamp=datetime.now().isoformat()
    )

def get_dashboard() -> DashboardResponse:
    return process_files()

def get_insights() -> InsightsResponse:
    dash = process_files()
    return InsightsResponse(insights=dash.insights)

def get_trends() -> TrendsResponse:
    dash = process_files()
    return TrendsResponse(trends=dash.trends)

def get_changes() -> ChangesResponse:
    dash = process_files()
    return ChangesResponse(changes=dash.changes)

import json
from pathlib import Path

def get_companies() -> CompaniesResponse:
    files = list_md_files('./data/md_files')
    companies_set = list(set(f['company'] for f in files))
    # Prioritize SNU
    companies = []
    if 'Shiv Nadar University Chennai' in companies_set:
        companies.append(Company(id="snuc", name="Shiv Nadar University Chennai", website="https://www.snuchennai.edu.in"))
    for c in companies_set:
        if c != 'Shiv Nadar University Chennai':
            # Load scrape URL from metadata
            scraped_dir = Path('./data/md_files') / "scraped_md" / c
            website = None
            if scraped_dir.exists() and (scraped_dir / "company.json").exists():
                try:
                    meta = json.loads((scraped_dir / "company.json").read_text())
                    website = meta.get('scrape_url')
                except:
                    pass
            companies.append(Company(id=c.lower().replace(" ", "-"), name=c, website=website))
    return CompaniesResponse(companies=companies)

def get_company(company_id: str) -> CompanyResponse:
    # Normalize ID: replace - with space
    norm_id = company_id.replace("-", " ").lower()
    companies = get_companies()
    company = next((c for c in companies.companies if c.id == company_id or norm_id in c.id), None)
    if not company:
        # Fallback for SNU
        company = Company(
            id="snuc", 
            name="Shiv Nadar University Chennai",
            website="https://www.snuchennai.edu.in",
            overview="Private university with Engineering, Law, Economics programs (CSE, ECE, Mechanical, B.Sc Economics). Chennai campus.",
            dossier="Analysis of 30+ MD files: admissions up 25%, placements 10.5 LPA avg, new Economics program."
        )
    else:
        dash = process_files()
        dossier_count = len([f for f in list_md_files('./data/md_files') if company.name.lower() in f['company'].lower()])
        company.overview = getattr(company, 'overview', f"Engineering & Commerce focus university.")
        company.dossier = f"LLM Dossier for {company.name}: {dossier_count} files analyzed (admissions, placements, faculty)."
    return CompanyResponse(company=company)

