import os
import glob
from typing import List, Dict
from pathlib import Path

import glob

def list_md_files(data_dir: str) -> List[Dict[str, str]]:
    """List all .md files in data_dir, infer company from path/prefix."""
    files = []
    md_pattern = os.path.join(data_dir, "**/*.md")
    for md_path in glob.glob(md_pattern, recursive=True):
        rel_path = os.path.relpath(md_path, data_dir)
        name = Path(rel_path).stem
        company_prefix = rel_path.split(os.sep)[0] if os.sep in rel_path else ''
        # Dynamic fallback + known mappings
        company_map = {
            'snuc': 'Shiv Nadar University Chennai',
            'scraped_md': 'Competitor University',
            'backend': 'Backend Data',
            'department': 'Engineering Department',
            '': 'Shiv Nadar University Chennai',
        }
        company = company_map.get(company_prefix, 'Shiv Nadar University Chennai')
        files.append({
            'name': name,
            'company': company,
            'path': md_path,
            'rel_path': rel_path
        })
    return files

def load_md_file(path: str) -> str:
    """Load content of MD file."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
