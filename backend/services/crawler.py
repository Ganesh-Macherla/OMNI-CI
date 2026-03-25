import asyncio
import hashlib
import json
import os
import difflib
import shutil
from pathlib import Path
from crawl4ai import AsyncWebCrawler
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def get_hash(content: str):
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def extract_clean_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return " ".join(soup.get_text().split())

async def scrape_competitor(start_url: str, company_dir: str, data_base: str = "backend/data/md_files", max_pages: int = 30) -> dict:
    """
    Scrape competitor site, save MD to data_base/scraped_md/{company_dir}/
    Returns: {'status': 'success', 'files_saved': int, 'company_dir': str}
    """
    output_dir = Path(data_base) / "scraped_md" / company_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    hash_file = output_dir / "hashes.json"
    visited = set()
    to_visit = [start_url]
    hashes = {}
    files_saved = 0
    
    if hash_file.exists():
        hashes = json.loads(hash_file.read_text())
    
    base_domain = urlparse(start_url).netloc
    
    async with AsyncWebCrawler() as crawler:
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)
            try:
                result = await crawler.arun(url=url)
                content_hash = get_hash(extract_clean_text(result.html))
                if hashes.get(url) != content_hash:
                    # Save MD
                    path = urlparse(url).path.strip("/") or "home"
                    filename = output_dir / f"{path.replace('/', '_')}.md"
                    filename.parent.mkdir(exist_ok=True)
                    filename.write_text(f"# Source: {url}\n\n{result.markdown}", encoding="utf-8")
                    files_saved += 1
                
                hashes[url] = content_hash
                
                # Follow internal links
                for link in result.links.get("internal", []):
                    full_url = urljoin(url, link.get("href"))
                    if base_domain in full_url and full_url not in visited:
                        to_visit.append(full_url)
                        
            except Exception as e:
                print(f"Crawl error {url}: {e}")
                continue
    
    # Save hashes
    hash_file.write_text(json.dumps(hashes, indent=2))
    
    # Save company metadata with user URL
    metadata = output_dir / "company.json"
    metadata.write_text(json.dumps({
        "name": company_dir,
        "scrape_url": start_url,
        "scraped_at": "2024-01-01T00:00:00", 
        "files_saved": files_saved,
        "total_pages": len(visited)
    }, indent=2))
    
    return {
        "status": "success",
        "company": company_dir,
        "files_saved": files_saved,
        "total_pages": len(visited),
        "output_dir": str(output_dir),
        "scrape_url": start_url
    }

