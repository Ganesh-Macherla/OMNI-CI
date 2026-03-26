from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import asyncio
import hashlib
import json
import re
import difflib
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path
from urllib.parse import urljoin, urlparse
from collections import defaultdict

# ── Optional deps ─────────────────────────────────────────────────────────────
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import anthropic as anthropic_sdk
    _anthropic_client = anthropic_sdk.Anthropic()
    ANTHROPIC_AVAILABLE = True
except Exception:
    _anthropic_client = None
    ANTHROPIC_AVAILABLE = False

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Market Intelligence API",
    description="Competitive intelligence engine — crawl, diff, and AI-analyze competitor sites.",
    version="2.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Storage paths ─────────────────────────────────────────────────────────────
DATA_DIR       = Path("data")
SNAPSHOTS_DIR  = DATA_DIR / "snapshots"
COMPANIES_FILE = DATA_DIR / "companies.json"
HASHES_FILE    = DATA_DIR / "hashes.json"
CHANGES_FILE   = DATA_DIR / "changes.json"
INSIGHTS_FILE  = DATA_DIR / "insights.json"
CRAWL_LOG_FILE = DATA_DIR / "crawl_log.json"

for d in [DATA_DIR, SNAPSHOTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

MAX_PAGES = 30

# ── Pydantic models ───────────────────────────────────────────────────────────

class AddCompanyRequest(BaseModel):
    name: str
    website: str
    industry: Optional[str] = ""
    target_segment: Optional[str] = ""
    geography: Optional[str] = ""
    pricing_model: Optional[str] = ""
    notes: Optional[str] = ""

class CrawlRequest(BaseModel):
    company_id: str
    url: str
    max_pages: Optional[int] = MAX_PAGES

class GenerateInsightsRequest(BaseModel):
    company_ids: Optional[List[str]] = None


# ── Core helpers ──────────────────────────────────────────────────────────────

def load_json(path: Path, default):
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def get_hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()

def url_slug(url: str) -> str:
    path = urlparse(url).path.strip("/") or "home"
    return re.sub(r"[^\w]", "_", path)[:80]

def company_id_from_name(name: str) -> str:
    return re.sub(r"[^\w]", "_", name.lower().strip())


# ── HTML extraction ───────────────────────────────────────────────────────────

def extract_clean_text(html: str) -> str:
    if BS4_AVAILABLE:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "head"]):
            tag.decompose()
        return " ".join(soup.get_text().split())
    return re.sub(r"<[^>]+>", " ", html)

def extract_sections(html: str) -> dict:
    if not BS4_AVAILABLE:
        return {}
    soup = BeautifulSoup(html, "html.parser")

    def _t(tag): return tag.get_text(" ", strip=True) if tag else ""

    hero = (_t(soup.find("h1")) or _t(soup.find("h2")))[:300]
    all_text = soup.get_text()
    pricing_mentions = list(set(re.findall(
        r'\$[\d,]+(?:\.\d{1,2})?(?:/mo(?:nth)?|/yr|/year|/user)?'
        r'|(?:free(?: trial| plan| tier)?|enterprise|contact (?:us|sales)|custom pricing)',
        all_text, re.I
    )))[:12]

    features = [
        li.get_text(" ", strip=True)[:150]
        for li in soup.find_all("li")
        if 10 < len(li.get_text(strip=True)) < 200
    ][:20]

    ctas = list({
        btn.get_text(strip=True)[:60]
        for btn in soup.find_all(["button", "a"])
        if btn.get("class") and re.search(r'btn|cta|button|primary|signup|start', " ".join(btn.get("class", [])), re.I)
        and btn.get_text(strip=True)
    })[:10]

    meta_tag = soup.find("meta", attrs={"name": "description"})
    meta_desc = (meta_tag.get("content", "") or "")[:300]
    headings = [h.get_text(" ", strip=True)[:150] for h in soup.find_all(["h2", "h3"])][:10]
    og = soup.find("meta", property="og:title")
    og_title = (og.get("content", "") if og else "")[:150]

    return {
        "hero_text": hero,
        "og_title": og_title,
        "meta_description": meta_desc,
        "headings": headings,
        "pricing_mentions": pricing_mentions,
        "features": features,
        "cta_buttons": ctas,
    }

def compute_diff(old_text: str, new_text: str) -> dict:
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    diff_lines = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
    added   = [l[1:].strip() for l in diff_lines if l.startswith("+") and not l.startswith("+++") and l[1:].strip()]
    removed = [l[1:].strip() for l in diff_lines if l.startswith("-") and not l.startswith("---") and l[1:].strip()]
    return {"added": added[:40], "removed": removed[:40], "change_score": len(added) + len(removed)}

def infer_change_type(url: str, diff: dict) -> str:
    url_lower = url.lower()
    combined  = " ".join(diff.get("added", []) + diff.get("removed", [])).lower()
    if re.search(r'pric|cost|fee|plan|tier|\$|billing', url_lower + combined):
        return "pricing"
    if re.search(r'product|feature|launch|release|new|integrat', url_lower + combined):
        return "feature"
    if re.search(r'about|mission|tagline|brand|voice|messaging|position', url_lower + combined):
        return "messaging"
    return "content"

def infer_impact_level(change_score: int, sections: dict) -> str:
    has_pricing = bool(sections.get("pricing_mentions"))
    if change_score > 40 or (change_score > 15 and has_pricing):
        return "high"
    if change_score > 10:
        return "medium"
    return "low"

def compute_sentiment_from_changes(changes: list) -> str:
    recent = [c for c in changes if c.get("date","") >= (datetime.utcnow() - timedelta(days=30)).date().isoformat()]
    high_count = sum(1 for c in recent if c.get("impact_level") == "high")
    if high_count >= 2:
        return "positive"
    return "neutral" if not recent else "neutral"

def _get_company_snapshots(company_id: str) -> list:
    snap_dir = SNAPSHOTS_DIR / company_id
    if not snap_dir.exists():
        return []
    return [load_json(f, {}) for f in snap_dir.glob("*.json") if load_json(f, {})]

def _company_name(company_id: str) -> str:
    companies = load_json(COMPANIES_FILE, [])
    c = next((c for c in companies if c["id"] == company_id), None)
    return c["name"] if c else company_id.replace("_", " ").title()

def _summarise_lines(lines: list) -> str:
    joined = " … ".join(l for l in lines[:5] if len(l) > 3)
    return joined[:300]


# ── AI helpers ────────────────────────────────────────────────────────────────

def _call_claude_json(system: str, user: str, max_tokens: int = 2000):
    if not ANTHROPIC_AVAILABLE or _anthropic_client is None:
        return None
    try:
        msg = _anthropic_client.messages.create(
            model="claude-opus-4-6",
            max_tokens=max_tokens,
            system=system + "\n\nRespond ONLY with valid JSON. No markdown, no explanation.",
            messages=[{"role": "user", "content": user}],
        )
        raw = msg.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except Exception as e:
        print(f"Claude API error: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# COMPANIES
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/companies", tags=["Companies"])
def list_companies(status: Optional[str] = None):
    companies = load_json(COMPANIES_FILE, [])
    if status:
        companies = [c for c in companies if c.get("status") == status]
    return {"companies": companies, "total": len(companies)}


@app.post("/api/companies", tags=["Companies"], status_code=201)
def add_company(req: AddCompanyRequest):
    """Register a new company. Provide name + website. Crawl separately via POST /api/crawl."""
    companies = load_json(COMPANIES_FILE, [])
    cid = company_id_from_name(req.name)
    if any(c["id"] == cid for c in companies):
        raise HTTPException(status_code=409, detail=f"Company '{cid}' already exists.")
    domain = urlparse(req.website).netloc.replace("www.", "")
    entry = {
        "id": cid, "name": req.name, "domain": domain,
        "website": str(req.website),
        "logo": f"https://logo.clearbit.com/{domain}",
        "industry": req.industry, "target_segment": req.target_segment,
        "geography": req.geography, "pricing_model": req.pricing_model,
        "notes": req.notes, "status": "active",
        "tracking_status": "Pending First Crawl",
        "sentiment": "neutral", "last_checked": None,
        "recent_changes": 0, "pages_tracked": 0,
        "added": datetime.utcnow().date().isoformat(),
    }
    companies.append(entry)
    save_json(COMPANIES_FILE, companies)
    return {"status": "added", "company": entry}


@app.get("/api/companies/{company_id}", tags=["Companies"])
def get_company(company_id: str):
    """Full company profile with real computed stats from crawl data."""
    companies = load_json(COMPANIES_FILE, [])
    company   = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found.")

    changes  = load_json(CHANGES_FILE, [])
    insights = load_json(INSIGHTS_FILE, [])
    company_changes  = sorted([ch for ch in changes  if ch["company_id"] == company_id], key=lambda x: x.get("date",""), reverse=True)
    company_insights = [i for i in insights if company_id in i.get("companies", [])]

    now     = datetime.utcnow()
    q_start = (now - timedelta(days=90)).date().isoformat()
    m_start = (now - timedelta(days=30)).date().isoformat()

    activity_summary = {
        "feature_launches_this_quarter":  sum(1 for c in company_changes if c.get("type") == "feature"  and c.get("date","") >= q_start),
        "pricing_updates_this_quarter":   sum(1 for c in company_changes if c.get("type") == "pricing"  and c.get("date","") >= q_start),
        "messaging_updates_this_quarter": sum(1 for c in company_changes if c.get("type") == "messaging" and c.get("date","") >= q_start),
        "content_updates_this_month":     sum(1 for c in company_changes if c.get("date","") >= m_start),
    }

    products = _derive_products_from_snapshots(company_id)
    launch_activity = [
        {"name": ch.get("after","")[:80] or ch.get("page",""), "date": ch["date"],
         "impact": ch["impact_level"].title() + " Impact", "type": ch["type"]}
        for ch in company_changes if ch.get("impact_level") in ("high","medium")
    ][:10]

    return {
        "company": company,
        "change_timeline": company_changes[:20],
        "company_insights": company_insights,
        "activity_summary": activity_summary,
        "products": products,
        "launch_activity": launch_activity,
        "snapshots_count": len(_get_company_snapshots(company_id)),
    }


@app.get("/api/companies/{company_id}/dossier", tags=["Companies"])
def get_company_dossier(company_id: str):
    return get_company(company_id)


@app.get("/api/companies/{company_id}/messaging", tags=["Companies"])
def get_company_messaging(company_id: str):
    companies = load_json(COMPANIES_FILE, [])
    if not any(c["id"] == company_id for c in companies):
        raise HTTPException(status_code=404, detail="Company not found.")
    changes = load_json(CHANGES_FILE, [])
    messaging_changes = sorted(
        [ch for ch in changes if ch["company_id"] == company_id and ch["type"] == "messaging"],
        key=lambda x: x.get("date",""), reverse=True
    )
    snapshots = _get_company_snapshots(company_id)
    hero_texts, all_headings, meta_descs = [], [], []
    for snap in snapshots:
        s = snap.get("sections", {})
        if s.get("hero_text"):     hero_texts.append(s["hero_text"])
        all_headings.extend(s.get("headings", []))
        if s.get("meta_description"): meta_descs.append(s["meta_description"])
    return {
        "company_id": company_id,
        "messaging_changes": messaging_changes,
        "current_signals": {
            "hero_texts":        list(dict.fromkeys(hero_texts))[:5],
            "key_headings":      list(dict.fromkeys(all_headings))[:15],
            "meta_descriptions": list(dict.fromkeys(meta_descs))[:3],
        },
        "total_messaging_changes": len(messaging_changes),
    }


@app.get("/api/companies/{company_id}/pricing", tags=["Companies"])
def get_company_pricing(company_id: str):
    companies = load_json(COMPANIES_FILE, [])
    if not any(c["id"] == company_id for c in companies):
        raise HTTPException(status_code=404, detail="Company not found.")
    changes = load_json(CHANGES_FILE, [])
    pricing_changes = sorted(
        [ch for ch in changes if ch["company_id"] == company_id and ch["type"] == "pricing"],
        key=lambda x: x.get("date",""), reverse=True
    )
    all_pricing = []
    for snap in _get_company_snapshots(company_id):
        all_pricing.extend(snap.get("sections", {}).get("pricing_mentions", []))
    return {
        "company_id": company_id,
        "pricing_mentions_across_site": list(set(all_pricing))[:20],
        "pricing_changes": pricing_changes,
        "total_pricing_changes": len(pricing_changes),
    }


@app.get("/api/companies/{company_id}/reviews", tags=["Companies"])
def get_company_reviews(company_id: str):
    """Returns crawled review page data. Crawl G2/Trustpilot/Reddit URLs to populate."""
    snapshots = _get_company_snapshots(company_id)
    review_snaps = [s for s in snapshots if re.search(r'g2\.com|trustpilot|reddit|gartner|capterra', s.get("url",""), re.I)]
    return {
        "company_id": company_id,
        "review_pages_crawled": len(review_snaps),
        "review_data": [
            {"url": s["url"], "scraped_at": s.get("scraped_at"),
             "text_preview": s.get("clean_text","")[:800],
             "features_extracted": s.get("sections",{}).get("features",[])[:10]}
            for s in review_snaps
        ],
        "note": "Add G2/Trustpilot/Reddit URLs via POST /api/crawl to populate this section.",
    }


def _derive_products_from_snapshots(company_id: str) -> list:
    snapshots = _get_company_snapshots(company_id)
    products = []
    for snap in snapshots:
        s    = snap.get("sections", {})
        hero = s.get("hero_text") or s.get("og_title") or ""
        if not hero or len(hero) < 5:
            continue
        url       = snap.get("url", "")
        page_path = urlparse(url).path.lower()
        if re.search(r'blog|news|press|career|legal|tos|privacy|cookie', page_path):
            continue
        try:
            days_ago = (datetime.utcnow() - datetime.fromisoformat(snap.get("scraped_at","").rstrip("Z"))).days
        except Exception:
            days_ago = 0
        products.append({
            "id": get_hash(url)[:8], "name": hero[:60], "url": url,
            "status": "New" if days_ago < 14 else "Core",
            "updated_days_ago": days_ago,
            "features": s.get("features", [])[:5],
            "pricing_mentions": s.get("pricing_mentions", []),
        })
    return products[:12]


# ══════════════════════════════════════════════════════════════════════════════
# CRAWL
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/crawl", tags=["Crawl"])
async def crawl_company(req: CrawlRequest, background_tasks: BackgroundTasks):
    """Trigger background crawl. Diffs against previous snapshot; records all changes."""
    if not CRAWL4AI_AVAILABLE:
        raise HTTPException(status_code=501, detail="crawl4ai not installed. Run: pip install crawl4ai && crawl4ai-setup")
    companies = load_json(COMPANIES_FILE, [])
    if not any(c["id"] == req.company_id for c in companies):
        raise HTTPException(status_code=404, detail=f"Company '{req.company_id}' not found. Add via POST /api/companies first.")
    background_tasks.add_task(_run_crawl, req.url, req.company_id, req.max_pages)
    return {"status": "started", "company_id": req.company_id, "url": req.url}


@app.get("/api/crawl/log", tags=["Crawl"])
def get_crawl_log(company_id: Optional[str] = None, limit: int = 50):
    log = load_json(CRAWL_LOG_FILE, [])
    if company_id:
        log = [e for e in log if e.get("company_id") == company_id]
    return {"log": log[-limit:], "total": len(log)}


async def _run_crawl(start_url: str, company_id: str, max_pages: int):
    hashes    = load_json(HASHES_FILE, {})
    changes   = load_json(CHANGES_FILE, [])
    crawl_log = load_json(CRAWL_LOG_FILE, [])
    visited   = set()
    to_visit  = [start_url]
    base_domain = urlparse(start_url).netloc
    snap_dir    = SNAPSHOTS_DIR / company_id
    snap_dir.mkdir(parents=True, exist_ok=True)
    new_changes = []

    async with AsyncWebCrawler() as crawler:
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)
            try:
                result     = await crawler.arun(url=url)
                clean_text = extract_clean_text(result.html)
                curr_hash  = get_hash(clean_text)
                sections   = extract_sections(result.html)
                snap_path  = snap_dir / f"{url_slug(url)}.json"

                if hashes.get(url) != curr_hash:
                    old_snap = load_json(snap_path, {})
                    old_text = old_snap.get("clean_text", "")
                    save_json(snap_path, {
                        "url": url, "company_id": company_id,
                        "scraped_at": now_iso(), "hash": curr_hash,
                        "clean_text": clean_text, "sections": sections,
                        "markdown": getattr(result, "markdown", ""),
                    })
                    if old_text:
                        diff = compute_diff(old_text, clean_text)
                        if diff["change_score"] > 5:
                            chg_type = infer_change_type(url, diff)
                            impact   = infer_impact_level(diff["change_score"], sections)
                            rec = {
                                "id": f"chg_{get_hash(url + now_iso())[:10]}",
                                "company_id": company_id,
                                "company_name": _company_name(company_id),
                                "date": datetime.utcnow().date().isoformat(),
                                "type": chg_type, "page": url,
                                "before": _summarise_lines(diff["removed"]),
                                "after":  _summarise_lines(diff["added"]),
                                "impact": "", "impact_level": impact,
                                "change_score": diff["change_score"],
                                "sections_after": {k: v for k, v in sections.items() if k in ("hero_text","pricing_mentions","cta_buttons")},
                            }
                            new_changes.append(rec)
                            changes.append(rec)
                    hashes[url] = curr_hash

                for link in getattr(result, "links", {}).get("internal", []):
                    full_url = urljoin(start_url, link.get("href",""))
                    parsed   = urlparse(full_url)
                    if (base_domain in parsed.netloc and full_url not in visited
                            and not re.search(r'\.(pdf|zip|png|jpg|svg|gif|ico|css|js)$', parsed.path, re.I)
                            and "#" not in full_url):
                        to_visit.append(full_url)

            except Exception as e:
                print(f"[crawl] Error on {url}: {e}")

    save_json(HASHES_FILE, hashes)
    save_json(CHANGES_FILE, changes)

    companies = load_json(COMPANIES_FILE, [])
    for c in companies:
        if c["id"] == company_id:
            c["last_checked"] = now_iso()
            c["tracking_status"] = "Active Tracking"
            c["pages_tracked"]   = len(visited)
            c["recent_changes"]  = sum(1 for ch in changes if ch["company_id"] == company_id)
            c["sentiment"]       = compute_sentiment_from_changes([ch for ch in changes if ch["company_id"] == company_id])
    save_json(COMPANIES_FILE, companies)

    crawl_log.append({
        "company_id": company_id, "start_url": start_url,
        "pages_visited": len(visited), "new_changes_detected": len(new_changes),
        "completed_at": now_iso(),
    })
    save_json(CRAWL_LOG_FILE, crawl_log)

    if ANTHROPIC_AVAILABLE and new_changes:
        await asyncio.get_event_loop().run_in_executor(None, _generate_and_save_insights, [company_id])


# ══════════════════════════════════════════════════════════════════════════════
# CHANGES
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/changes", tags=["Changes"])
def list_changes(
    company_id:  Optional[str] = None,
    change_type: Optional[str] = None,
    days:        int = 90,
    impact:      Optional[str] = None,
    page:        int = 1,
    page_size:   int = 20,
):
    """Change feed from real crawl diffs. Filters: company_id, change_type, days, impact."""
    changes = load_json(CHANGES_FILE, [])
    cutoff  = (datetime.utcnow() - timedelta(days=days)).date().isoformat()

    def passes(ch):
        if company_id  and ch.get("company_id")  != company_id:  return False
        if change_type and ch.get("type")         != change_type: return False
        if impact      and ch.get("impact_level") != impact:      return False
        if ch.get("date","9999") < cutoff:                        return False
        return True

    filtered = sorted([ch for ch in changes if passes(ch)], key=lambda x: x.get("date",""), reverse=True)
    total = len(filtered)
    start = (page - 1) * page_size
    return {"changes": filtered[start:start+page_size], "total": total, "page": page, "page_size": page_size}


@app.get("/api/changes/{change_id}", tags=["Changes"])
def get_change(change_id: str):
    changes = load_json(CHANGES_FILE, [])
    ch = next((c for c in changes if c["id"] == change_id), None)
    if not ch:
        raise HTTPException(status_code=404, detail="Change not found.")
    return ch


# ══════════════════════════════════════════════════════════════════════════════
# SNAPSHOTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/snapshots/{company_id}", tags=["Snapshots"])
def list_snapshots(company_id: str):
    snaps = _get_company_snapshots(company_id)
    return {
        "company_id": company_id, "total": len(snaps),
        "snapshots": [
            {"url": s.get("url"), "scraped_at": s.get("scraped_at"),
             "hero_text": s.get("sections",{}).get("hero_text","")[:120],
             "pricing_mentions": s.get("sections",{}).get("pricing_mentions",[])[:4],
             "hash": s.get("hash","")[:12]}
            for s in sorted(snaps, key=lambda x: x.get("scraped_at",""), reverse=True)
        ],
    }


@app.get("/api/snapshots/{company_id}/page", tags=["Snapshots"])
def get_snapshot(company_id: str, url: str = Query(...)):
    snap_path = SNAPSHOTS_DIR / company_id / f"{url_slug(url)}.json"
    if not snap_path.exists():
        raise HTTPException(status_code=404, detail="No snapshot for this URL. Crawl it first.")
    snap = load_json(snap_path, {})
    return {
        "url": snap.get("url"), "company_id": company_id,
        "scraped_at": snap.get("scraped_at"), "hash": snap.get("hash"),
        "sections": snap.get("sections", {}),
        "text_preview": snap.get("clean_text","")[:600],
        "markdown_preview": snap.get("markdown","")[:600],
    }


# ══════════════════════════════════════════════════════════════════════════════
# INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/insights", tags=["Insights"])
def list_insights(
    priority: Optional[str] = None, insight_type: Optional[str] = None, company_id: Optional[str] = None,
):
    insights = load_json(INSIGHTS_FILE, [])
    def passes(i):
        if priority     and i.get("priority") != priority:            return False
        if insight_type and i.get("type")     != insight_type:        return False
        if company_id   and company_id not in i.get("companies", []): return False
        return True
    filtered = sorted([i for i in insights if passes(i)],
        key=lambda x: ({"high":0,"medium":1,"low":2}.get(x.get("priority","low"),3), x.get("created_at","")))
    stats = {
        "total": len(insights),
        "high_priority": sum(1 for i in insights if i.get("priority") == "high"),
        "opportunities":  sum(1 for i in insights if i.get("type") == "Opportunities"),
        "threats":        sum(1 for i in insights if i.get("type") == "Threats"),
    }
    return {"insights": filtered, "total": len(filtered), "stats": stats}


@app.get("/api/insights/{insight_id}", tags=["Insights"])
def get_insight(insight_id: str):
    insights = load_json(INSIGHTS_FILE, [])
    i = next((x for x in insights if x["id"] == insight_id), None)
    if not i:
        raise HTTPException(status_code=404, detail="Insight not found.")
    return i


@app.post("/api/insights/generate", tags=["Insights"])
def generate_insights(req: GenerateInsightsRequest):
    """Use Claude to generate strategic insights from real detected changes."""
    if not ANTHROPIC_AVAILABLE:
        raise HTTPException(status_code=501, detail="Set ANTHROPIC_API_KEY and install anthropic SDK.")
    company_ids = req.company_ids
    if not company_ids:
        company_ids = [c["id"] for c in load_json(COMPANIES_FILE, [])]
    new = _generate_and_save_insights(company_ids)
    return {"status": "generated", "new_insights_count": len(new), "insights": new}


def _generate_and_save_insights(company_ids: list) -> list:
    changes = load_json(CHANGES_FILE, [])
    cutoff  = (datetime.utcnow() - timedelta(days=60)).date().isoformat()
    relevant = [ch for ch in changes if ch.get("company_id") in company_ids and ch.get("date","") >= cutoff]
    if not relevant:
        return []

    company_summaries = defaultdict(list)
    for ch in relevant:
        company_summaries[ch["company_id"]].append(
            f"[{ch['date']}] {ch['type'].upper()} on {ch['page']}: "
            f"Before: {ch.get('before','—')[:150]} | After: {ch.get('after','—')[:150]} "
            f"(impact: {ch.get('impact_level','?')})"
        )

    summary_text = "\n\n".join(
        f"Company: {_company_name(cid)}\n" + "\n".join(events)
        for cid, events in company_summaries.items()
    )

    system = (
        "You are a senior competitive intelligence analyst. "
        "Produce concise, actionable strategic insights grounded strictly in the provided evidence."
    )
    user = f"""
Analyze these real competitor website changes and produce 4-8 strategic insights.

CHANGES:
{summary_text}

Return a JSON array. Each object must have exactly:
- id: "ins_" + 8 random hex chars
- title: one punchy sentence (max 15 words)
- summary: 2-3 sentence elaboration
- evidence: specific data point from the changes above
- recommended_action: concrete next step for the reader's team
- priority: "high" | "medium" | "low"
- type: "Opportunities" | "Threats" | "Trends"
- companies: array of company_ids involved
- source_change_ids: array of cited change IDs ([] if none)
- created_at: current ISO8601 timestamp
"""

    result = _call_claude_json(system, user, max_tokens=3000)
    if not result or not isinstance(result, list):
        return []

    existing     = load_json(INSIGHTS_FILE, [])
    existing_ids = {i["id"] for i in existing}
    truly_new    = []
    for ins in result:
        if not isinstance(ins, dict) or not ins.get("id") or not ins.get("title"):
            continue
        if ins["id"] in existing_ids:
            ins["id"] = f"ins_{get_hash(ins['title'] + now_iso())[:8]}"
        ins.setdefault("created_at", now_iso())
        ins.setdefault("companies", [])
        ins.setdefault("source_change_ids", [])
        truly_new.append(ins)

    save_json(INSIGHTS_FILE, existing + truly_new)
    return truly_new


# ══════════════════════════════════════════════════════════════════════════════
# TRENDS  (computed from real snapshot + change data)
# ══════════════════════════════════════════════════════════════════════════════

THEME_KEYWORDS = {
    "AI & Machine Learning":  ["ai", "machine learning", "ml", "artificial intelligence", "neural", "llm", "generative", "fraud detection", "prediction", "automation"],
    "Embedded Finance":       ["embedded finance", "embedded payment", "banking as a service", "baas", "platform banking", "fintech api"],
    "Crypto Integration":     ["crypto", "cryptocurrency", "bitcoin", "ethereum", "blockchain", "web3", "stablecoin", "digital currency"],
    "Vertical Solutions":     ["healthcare", "hospitality", "retail", "restaurant", "e-commerce", "marketplace", "saas", "vertical"],
    "Instant Settlement":     ["instant settlement", "real-time", "same-day", "faster payment", "instant payout", "rtp"],
    "Developer Experience":   ["api", "sdk", "documentation", "developer", "open source", "webhook", "integration"],
    "BNPL / Financing":       ["buy now pay later", "bnpl", "installment", "financing", "split pay", "pay later"],
}


@app.get("/api/trends", tags=["Trends"])
def get_trends():
    return {
        "emerging_themes":         _compute_emerging_themes(),
        "messaging_theme_trends":  _compute_messaging_trends(),
        "feature_signals":         _compute_feature_signals(),
        "overused_claims":         _compute_overused_claims(),
        "competitive_positioning": _compute_positioning(),
    }

@app.get("/api/trends/emerging-themes", tags=["Trends"])
def get_emerging_themes():
    return {"themes": _compute_emerging_themes()}

@app.get("/api/trends/messaging", tags=["Trends"])
def get_messaging_trends():
    return {"series": _compute_messaging_trends()}

@app.get("/api/trends/feature-adoption", tags=["Trends"])
def get_feature_adoption():
    return _compute_feature_signals()

@app.get("/api/trends/positioning", tags=["Trends"])
def get_competitive_positioning():
    return {"positioning": _compute_positioning()}

@app.get("/api/trends/overused-claims", tags=["Trends"])
def get_overused_claims():
    return {"claims": _compute_overused_claims()}


def _compute_emerging_themes() -> list:
    changes   = load_json(CHANGES_FILE, [])
    companies = load_json(COMPANIES_FILE, [])
    if not changes and not companies:
        return []

    now           = datetime.utcnow()
    recent_cutoff = (now - timedelta(days=30)).date().isoformat()
    prior_cutoff  = (now - timedelta(days=60)).date().isoformat()

    theme_counts = {t: {"recent": 0, "prior": 0, "companies": set()} for t in THEME_KEYWORDS}

    all_sources = []
    for ch in changes:
        text = f"{ch.get('before','')} {ch.get('after','')} {ch.get('page','')}".lower()
        all_sources.append((text, ch.get("date",""), ch.get("company_id","")))

    for c in companies:
        for snap in _get_company_snapshots(c["id"]):
            s    = snap.get("sections", {})
            text = " ".join([s.get("hero_text",""), " ".join(s.get("headings",[])),
                             " ".join(s.get("features",[])), s.get("meta_description","")]).lower()
            all_sources.append((text, snap.get("scraped_at","")[:10], c["id"]))

    for text, date, cid in all_sources:
        for theme, keywords in THEME_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                theme_counts[theme]["companies"].add(cid)
                if date >= recent_cutoff:   theme_counts[theme]["recent"] += 1
                elif date >= prior_cutoff:  theme_counts[theme]["prior"]  += 1

    themes = []
    for i, (theme, counts) in enumerate(theme_counts.items()):
        total = counts["recent"] + counts["prior"]
        if total == 0:
            continue
        prior  = max(counts["prior"], 1)
        growth = round(((counts["recent"] - prior) / prior) * 100)
        themes.append({
            "id": f"t{i+1}", "name": theme, "growth_pct": growth, "mentions": total,
            "recent_mentions": counts["recent"],
            "companies": [_company_name(cid) for cid in counts["companies"]][:5],
            "category": "High Growth" if growth > 50 else ("Growing" if growth > 0 else "Declining"),
        })

    themes.sort(key=lambda x: x["growth_pct"], reverse=True)
    return themes[:8]


def _compute_messaging_trends() -> list:
    changes = load_json(CHANGES_FILE, [])
    now     = datetime.utcnow()
    months  = [(now - timedelta(days=30 * i)).strftime("%b") for i in range(5, -1, -1)]
    month_keys = [(now - timedelta(days=30 * i)).strftime("%Y-%m") for i in range(5, -1, -1)]

    result = []
    for label, ym in zip(months, month_keys):
        row = {"month": label}
        for theme, keywords in THEME_KEYWORDS.items():
            count = sum(
                1 for ch in changes
                if ch.get("date","")[:7] == ym
                and any(kw in f"{ch.get('before','')} {ch.get('after','')}".lower() for kw in keywords)
            )
            row[re.sub(r"[^\w]", "_", theme.lower())[:20]] = count
        result.append(row)
    return result


def _compute_feature_signals() -> dict:
    companies = load_json(COMPANIES_FILE, [])
    if not companies:
        return {"features": [], "companies": {}}

    feature_buckets = list(THEME_KEYWORDS.keys())
    company_scores  = {}
    for c in companies:
        snaps = _get_company_snapshots(c["id"])
        if not snaps:
            continue
        all_text = " ".join(
            " ".join([s.get("sections",{}).get("hero_text",""),
                      " ".join(s.get("sections",{}).get("features",[])),
                      " ".join(s.get("sections",{}).get("headings",[]))]).lower()
            for s in snaps
        )
        scores = [min(100, round((sum(1 for kw in THEME_KEYWORDS[t] if kw in all_text) / len(THEME_KEYWORDS[t])) * 100))
                  for t in feature_buckets]
        company_scores[c["name"]] = scores
    return {"features": feature_buckets, "companies": company_scores}


def _compute_overused_claims() -> list:
    companies = load_json(COMPANIES_FILE, [])
    if not companies:
        return []

    PHRASES = [
        ("seamless integration",  "Integration claim that every vendor makes"),
        ("enterprise-grade",      "Security/quality table stake, not differentiating"),
        ("easy to use",           "Vague without specific usability evidence"),
        ("global coverage",       "Most major players now offer multi-country support"),
        ("24/7 support",          "Support availability, not quality"),
        ("no hidden fees",        "Still meaningful — pricing transparency resonates"),
        ("developer-first",       "Differentiating only if backed by strong docs"),
        ("real-time",             "Broad claim — needs specifics for credibility"),
        ("all-in-one",            "Effective only with strong product breadth"),
        ("trusted by",            "Social proof that needs specifics to land"),
    ]

    phrase_data = []
    for phrase, verdict in PHRASES:
        users = [c["name"] for c in companies
                 if any(phrase.lower() in (snap.get("clean_text","") or "").lower()
                        for snap in _get_company_snapshots(c["id"]))]
        saturation = round((len(users) / max(len(companies), 1)) * 100)
        phrase_data.append({
            "phrase": f'"{phrase.title()}"',
            "uses": len(users),
            "saturation_pct": saturation,
            "verdict": verdict,
            "companies_using": users,
            "trend": "flat",
        })

    phrase_data.sort(key=lambda x: x["saturation_pct"], reverse=True)
    return phrase_data


def _compute_positioning() -> list:
    companies   = load_json(COMPANIES_FILE, [])
    DEV_KEYWORDS = ["api","sdk","developer","documentation","webhook","open source","cli","github","npm","library"]
    ENT_KEYWORDS = ["enterprise","compliance","sla","soc 2","gdpr","hipaa","audit","role-based","dedicated","white glove"]
    COLORS = ["#6366f1","#22c55e","#f59e0b","#ef4444","#a855f7","#06b6d4","#f97316","#ec4899"]

    result = []
    for i, c in enumerate(companies):
        snaps = _get_company_snapshots(c["id"])
        if not snaps:
            continue
        all_text = " ".join((snap.get("clean_text","") or "").lower() for snap in snaps)
        dev_score = min(100, round((sum(1 for kw in DEV_KEYWORDS if kw in all_text) / len(DEV_KEYWORDS)) * 100))
        ent_score = min(100, round((sum(1 for kw in ENT_KEYWORDS if kw in all_text) / len(ENT_KEYWORDS)) * 100))
        result.append({"company": c["name"], "developer_experience": dev_score, "enterprise_features": ent_score, "color": COLORS[i % len(COLORS)]})
    return result


# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/overview", tags=["Overview"])
def get_overview():
    companies = load_json(COMPANIES_FILE, [])
    insights  = load_json(INSIGHTS_FILE, [])
    changes   = load_json(CHANGES_FILE,  [])
    crawl_log = load_json(CRAWL_LOG_FILE, [])

    now     = datetime.utcnow()
    w_start = (now - timedelta(days=7)).date().isoformat()

    monthly_trend = []
    for offset in range(5, -1, -1):
        dt  = now - timedelta(days=30 * offset)
        ym  = dt.strftime("%Y-%m")
        monthly_trend.append({
            "month":               dt.strftime("%b"),
            "competitor_mentions": sum(1 for ch in changes if ch.get("date","")[:7] == ym),
            "product_launches":    sum(1 for ch in changes if ch.get("date","")[:7] == ym and ch.get("type") == "feature"),
            "pricing_changes":     sum(1 for ch in changes if ch.get("date","")[:7] == ym and ch.get("type") == "pricing"),
        })

    recent_updates = []
    for entry in reversed(crawl_log[-10:]):
        recent_updates.append({
            "text": f"Crawl done — {entry.get('new_changes_detected',0)} changes detected",
            "company": _company_name(entry.get("company_id","")),
            "time": entry.get("completed_at",""),
        })
    for ch in sorted([c for c in changes if c.get("date","") >= w_start], key=lambda x: x.get("date",""), reverse=True)[:5]:
        recent_updates.append({
            "text": f"{ch.get('type','').title()} change: {(ch.get('after','') or '')[:60]}",
            "company": ch.get("company_name",""), "time": ch.get("date",""),
        })
    recent_updates = sorted(recent_updates, key=lambda x: x.get("time",""), reverse=True)[:10]

    return {
        "tracked_companies":      len(companies),
        "active_insights":        len(insights),
        "market_changes":         len(changes),
        "opportunities":          sum(1 for i in insights if i.get("type") == "Opportunities"),
        "new_changes_this_week":  sum(1 for ch in changes if ch.get("date","") >= w_start),
        "market_activity_trends": monthly_trend,
        "recent_updates":         recent_updates,
        "tracked_companies_list": [
            {"id": c["id"], "name": c["name"], "logo": c.get("logo",""),
             "sentiment": c.get("sentiment","neutral"), "last_checked": c.get("last_checked"),
             "recent_changes": c.get("recent_changes",0), "tracking_status": c.get("tracking_status","")}
            for c in companies
        ],
        "recent_insights": sorted(insights, key=lambda x: x.get("created_at",""), reverse=True)[:3],
    }


# ══════════════════════════════════════════════════════════════════════════════
# SEARCH
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/search", tags=["Search"])
def search(q: str = Query(..., min_length=2)):
    q_lower = q.lower()
    results = {"companies": [], "insights": [], "changes": []}
    for c in load_json(COMPANIES_FILE, []):
        if q_lower in f"{c.get('name','')} {c.get('industry','')} {c.get('domain','')}".lower():
            results["companies"].append({"id": c["id"], "name": c["name"], "domain": c.get("domain","")})
    for i in load_json(INSIGHTS_FILE, []):
        if q_lower in f"{i.get('title','')} {i.get('summary','')} {i.get('evidence','')}".lower():
            results["insights"].append({"id": i["id"], "title": i["title"], "priority": i.get("priority","")})
    for ch in load_json(CHANGES_FILE, []):
        if q_lower in f"{ch.get('before','')} {ch.get('after','')} {ch.get('page','')}".lower():
            results["changes"].append({"id": ch["id"], "company": ch.get("company_name",""), "type": ch.get("type",""), "date": ch.get("date","")})
    return {"query": q, "total": sum(len(v) for v in results.values()), "results": results}


# ══════════════════════════════════════════════════════════════════════════════
# HEALTH
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "crawl4ai_available":  CRAWL4AI_AVAILABLE,
        "bs4_available":       BS4_AVAILABLE,
        "anthropic_available": ANTHROPIC_AVAILABLE,
        "data_dir":            str(DATA_DIR.resolve()),
        "companies_count":     len(load_json(COMPANIES_FILE, [])),
        "changes_count":       len(load_json(CHANGES_FILE,   [])),
        "insights_count":      len(load_json(INSIGHTS_FILE,  [])),
        "snapshots_size_bytes": sum(f.stat().st_size for f in SNAPSHOTS_DIR.rglob("*.json") if f.is_file()),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
