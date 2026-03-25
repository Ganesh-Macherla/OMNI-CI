import os
import httpx
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

async def cerebras_chat(prompt: str, model: str = "llama-3.1-70b-versatile") -> str:
    """Call Cerebras API."""
    api_key = os.getenv('CSK_API_KEY')
    if not api_key:
        raise ValueError("CSK_API_KEY not set")
    
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 2000
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=data, headers=headers)
            resp.raise_for_status()
            return resp.json()['choices'][0]['message']['content']
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            # Fallback mock for testing
            return '{"insights": [{"title": "Fallback Insight", "description": "Backend LLM API unavailable - using fallback", "impact": "low", "evidence": "API 404", "recommended_action": "Check Cerebras API key", "source": "system"}], "trends": [], "changes": [], "companies": ["Shiv Nadar Univ Chennai"]}'
        raise

SELECT_PROMPT = '''From these competitor files: {files}
Select top 5 most relevant for market intelligence analysis (focus on changes in admissions, placements, programs, messaging).
Respond with JSON array of filenames only: ["file1.md", "file2.md"]'''

ANALYZE_PROMPT = '''Analyze these competitor MD files content for market intel:

{contents}

Generate structured insights as JSON matching this schema:
{{
  "insights": [{{"title": "", "description": "", "impact": "high|medium|low", "evidence": "", "recommended_action": "", "source": ""}}],
  "trends": [{{"title": "", "description": "", "type": "pricing|messaging|feature", "source": ""}}],
  "changes": [{{"title": "", "description": "", "type": "added|removed|updated", "source": ""}}],
  "companies": ["company1", "company2"]
}}

Focus on: pricing changes, messaging themes, pain points, whitespace opportunities, competitor positioning.'''

async def select_files(files: List[Dict[str, str]]) -> List[str]:
    file_list = ', '.join([f['rel_path'] for f in files])
    prompt = SELECT_PROMPT.format(files=file_list)
    response = await cerebras_chat(prompt)
    import json
    try:
        selected = json.loads(response)
        return selected
    except:
        return [f['rel_path'] for f in files[:5]]  # fallback

async def analyze_contents(contents: List[Dict[str, Any]]) -> Dict:
    content_str = '\\n---\\n'.join([f"File: {c['rel_path']}\\n{c['content'][:2000]}" for c in contents])
    prompt = ANALYZE_PROMPT.format(contents=content_str)
    response = await cerebras_chat(prompt)
    import json
    try:
        return json.loads(response)
    except:
        return {"insights": [], "trends": [], "changes": [], "companies": []}
