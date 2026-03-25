import asyncio
import hashlib
import json
import os
import difflib
import shutil
from crawl4ai import AsyncWebCrawler
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

BASE_DOMAIN = "snuchennai.edu.in"
MAX_PAGES = 30
OUTPUT_DIR = "snuc"
HASH_FILE = "hashes1.json"

def get_hash(content: str):
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def extract_clean_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return " ".join(soup.get_text().split())

def save_markdown(url, content):
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    path = urlparse(url).path.strip("/") or "home"
    filename = os.path.join(OUTPUT_DIR, f"{path.replace('/', '_')}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Source: {url}\n\n{content}")

async def crawl_site(start_url):
    visited = set()
    to_visit = [start_url]
    hashes = {}
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f: hashes = json.load(f)

    async with AsyncWebCrawler() as crawler:
        while to_visit and len(visited) < MAX_PAGES:
            url = to_visit.pop(0)
            if url in visited: continue
            visited.add(url)
            try:
                result = await crawler.arun(url=url)
                current_hash = get_hash(extract_clean_text(result.html))
                if hashes.get(url) != current_hash:
                    save_markdown(url, result.markdown)
                hashes[url] = current_hash
                for link in result.links.get("internal", []):
                    full_url = urljoin(url, link.get("href"))
                    if BASE_DOMAIN in full_url and full_url not in visited:
                        to_visit.append(full_url)
            except Exception as e: print(f"Error: {e}")

    with open(HASH_FILE, "w") as f: json.dump(hashes, f, indent=2)

def generate_diff():
    if not os.path.exists("hashes_baseline.json"): return
    with open("hashes_baseline.json") as f1, open("hashes1.json") as f2:
        diff = difflib.unified_diff(f1.readlines(), f2.readlines(), linterm='')
    with open("crawl_diff.txt", "w") as f: f.write("\n".join(list(diff)))

if __name__ == "__main__":
    if os.path.exists(HASH_FILE): shutil.copy(HASH_FILE, "hashes_baseline.json")
    asyncio.run(crawl_site("https://www.snuchennai.edu.in/"))
    generate_diff()
