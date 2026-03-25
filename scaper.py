import asyncio
import hashlib
import json
from crawl4ai import AsyncWebCrawler
from urllib.parse import urljoin, urlparse
import os
from bs4 import BeautifulSoup

BASE_DOMAIN = "snuchennai.edu.in"
MAX_PAGES = 30
OUTPUT_DIR = "snuc"
HASH_FILE = "hashes1.json"

visited = set()

# HASH FUNCTION
def get_hash(content: str):
    return hashlib.md5(content.encode("utf-8")).hexdigest()

# LOAD / SAVE HASHES
def load_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            return json.load(f)
    return {}

def save_hashes(hashes):
    with open(HASH_FILE, "w") as f:
        json.dump(hashes, f, indent=2)

# CLEAN CONTENT (for hashing)
def extract_clean_text(html):
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts/styles
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    return " ".join(text.split())

# CLEAN FILE NAME
def make_filename(url):
    path = urlparse(url).path.strip("/")
    if not path:
        path = "home"
    filename = path.replace("/", "_")
    return f"{filename}.md"

# SAVE MARKDOWN
def save_markdown(url, content):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    filename = make_filename(url)
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Source: {url}\n\n")
        f.write(content)

    print(f"Saved: {filepath}")

# CRAWLER
async def crawl_site(start_url):
    to_visit = [start_url]
    hashes = load_hashes()

    async with AsyncWebCrawler() as crawler:

        while to_visit and len(visited) < MAX_PAGES:
            url = to_visit.pop(0)

            if url in visited:
                continue

            visited.add(url)
            print(f"🔍 Crawling: {url}")

            try:
                result = await crawler.arun(url=url, wait_for='networkidle')
                markdown = result.markdown
                html = result.html

                if not html:
                    continue

                # HASHING (use CLEAN TEXT)
                clean_text = extract_clean_text(html)
                current_hash = get_hash(clean_text)
                old_hash = hashes.get(url)

                if old_hash:
                    if old_hash == current_hash:
                        print("✅ No change")
                    else:
                        print("⚠️ Content changed")
                else:
                    print("🆕 New page")

                hashes[url] = current_hash

                # SAVE MARKDOWN
                if markdown and len(markdown) > 50:
                    save_markdown(url, markdown)

                # LINK EXTRACTION
                for link in result.links.get("internal", []):
                    href = link.get("href")
                    if not href:
                        continue

                    full_url = urljoin(url, href)

                    if BASE_DOMAIN in urlparse(full_url).netloc:
                        if full_url not in visited:
                            to_visit.append(full_url)

            except Exception as e:
                print("❌ Error:", e)

    save_hashes(hashes)

# RUN
async def main():
    start_url = "https://www.snuchennai.edu.in/"
    await crawl_site(start_url)
    print("\n✅ All pages processed!")

asyncio.run(main())