"""Helper utilities."""

import hashlib
import re
from typing import Any, Dict, List
from pathlib import Path


def generate_hash(content: str) -> str:
    """Generate MD5 hash of content."""
    return hashlib.md5(content.encode()).hexdigest()


def clean_filename(filename: str) -> str:
    """Clean filename for safe storage."""
    # Remove special characters except dots and hyphens
    cleaned = re.sub(r'[^\w\-_\.]', '_', filename)
    return cleaned


def parse_markdown_headers(content: str) -> List[Dict[str, Any]]:
    """Parse markdown headers from content."""
    headers = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if line.strip().startswith('#'):
            header_match = re.match(r'^(#+)\s*(.+)', line.strip())
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                headers.append({
                    'level': level,
                    'title': title,
                    'line': i + 1
                })
    
    return headers


def extract_code_blocks(content: str) -> List[Dict[str, Any]]:
    """Extract code blocks from markdown content."""
    code_blocks = []
    lines = content.split('\n')
    in_code_block = False
    current_block = []
    start_line = 0
    language = ""
    
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            if not in_code_block:
                # Starting code block
                in_code_block = True
                start_line = i + 1
                language = line.strip()[3:].strip()
                current_block = []
            else:
                # Ending code block
                in_code_block = False
                code_blocks.append({
                    'language': language,
                    'content': '\n'.join(current_block),
                    'start_line': start_line,
                    'end_line': i,
                    'line_count': len(current_block)
                })
                current_block = []
        elif in_code_block:
            current_block.append(line)
    
    return code_blocks


def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate JSON data has required fields."""
    return all(field in data for field in required_fields)


def safe_get_nested(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Safely get nested dictionary value using dot notation."""
    keys = path.split('.')
    current = data
    
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default