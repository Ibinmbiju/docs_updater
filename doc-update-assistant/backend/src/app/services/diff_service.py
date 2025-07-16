# Diff service
"""Diff service for generating GitHub-style diffs."""

import difflib
import re
from typing import Dict, List

from ..models.suggestion import DiffHunk


class DiffService:
    """Handles diff generation and parsing (GitHub-style)."""
    
    @staticmethod
    def generate_diff_hunks(
        original: str, 
        suggested: str, 
        context_lines: int = 3
    ) -> List[DiffHunk]:
        """Generate diff hunks between original and suggested content."""
        original_lines = original.splitlines()
        suggested_lines = suggested.splitlines()
        diff = difflib.unified_diff(
            original_lines,
            suggested_lines,
            lineterm='',
            n=context_lines
        )
        return DiffService._process_diff_lines(diff)

    @staticmethod
    def _process_diff_lines(diff) -> List[DiffHunk]:
        """Process diff lines and create hunks."""
        hunks = []
        current_hunk = None
        for line in diff:
            if line.startswith('@@'):
                if current_hunk:
                    hunks.append(current_hunk)
                current_hunk = DiffService._parse_hunk_header(line)
            elif current_hunk:
                DiffService._add_line_to_hunk(current_hunk, line)
        if current_hunk:
            hunks.append(current_hunk)
        return hunks

    @staticmethod
    def _add_line_to_hunk(hunk: DiffHunk, line: str) -> None:
        """Add a line to the current hunk based on its type."""
        if line.startswith('-'):
            hunk.old_lines.append(line[1:])
        elif line.startswith('+'):
            hunk.new_lines.append(line[1:])
        elif line.startswith(' '):
            context_line = line[1:]
            hunk.old_lines.append(context_line)
            hunk.new_lines.append(context_line)
    
    @staticmethod
    def _parse_hunk_header(header: str) -> DiffHunk:
        """Parse a hunk header like @@ -1,4 +1,6 @@."""
        # Extract the numbers from the header
        match = re.match(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', header)
        if not match:
            raise ValueError(f"Invalid hunk header: {header}")
            
        old_start = int(match.group(1))
        old_count = int(match.group(2)) if match.group(2) else 1
        new_start = int(match.group(3))
        new_count = int(match.group(4)) if match.group(4) else 1
        
        return DiffHunk(
            old_start=old_start,
            old_count=old_count,
            new_start=new_start,
            new_count=new_count,
            old_lines=[],
            new_lines=[]
        )
    
    @staticmethod
    def apply_diff_hunks(original: str, hunks: List[DiffHunk]) -> str:
        """Apply diff hunks to original content."""
        # TODO: Implement proper diff application
        # For now, this is a placeholder
        return original
    
    @staticmethod
    def get_diff_stats(hunks: List[DiffHunk]) -> Dict[str, int]:
        """Get diff statistics (additions, deletions, etc.)."""
        additions = sum(len([line for line in hunk.new_lines if line not in hunk.old_lines]) for hunk in hunks)
        deletions = sum(len([line for line in hunk.old_lines if line not in hunk.new_lines]) for hunk in hunks)
        return {
            "additions": additions,
            "deletions": deletions,
            "changes": len(hunks)
        }