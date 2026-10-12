"""Resolve the immutable source snapshot reviewed before the LLM findings."""

import hashlib
from pathlib import Path

from check_standards_clause_revision import CURRENT_PATHS, verify_current_sources
from check_a2a_did_adoption import prior_path as at_a2a_did_base


HISTORY = Path('verification/history/llm-review-target-2026-09-25')
STANDARDS_HISTORY = Path('verification/history/standards-clauses-base-2026-09-29')


def pinned_path(root, name, digest):
    historical = root / HISTORY / name
    older = root / STANDARDS_HISTORY / name
    path = historical if historical.is_file() else (
        older if name in CURRENT_PATHS and older.is_file() else at_a2a_did_base(root, name))
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('review target identity: ' + name)
    if (root / 'verification/standards-clause-revision.json').is_file():
        verify_current_sources(root)
    return path
