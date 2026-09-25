"""Resolve the immutable source snapshot reviewed before the LLM findings."""

import hashlib
from pathlib import Path


HISTORY = Path('verification/history/llm-review-target-2026-09-25')


def pinned_path(root, name, digest):
    historical = root / HISTORY / name
    path = historical if historical.is_file() else root / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('review target identity: ' + name)
    return path
