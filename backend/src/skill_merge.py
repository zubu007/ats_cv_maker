"""Helpers for merging skill keywords without duplicate overlap."""

from __future__ import annotations

import re
from typing import Iterable

_SPLIT_PATTERN = re.compile(r"[,;\n]")


def split_skills(raw_skills: str) -> list[str]:
    """Split comma/newline/semicolon skill text into clean values."""
    if not raw_skills:
        return []

    skills: list[str] = []
    for item in _SPLIT_PATTERN.split(raw_skills):
        cleaned = item.strip().strip("-•")
        if cleaned:
            skills.append(cleaned)
    return skills


def _normalize_skill_key(skill: str) -> str:
    """Normalize a skill for overlap checks (case-insensitive, punctuation-agnostic)."""
    lowered = skill.lower().strip()
    return re.sub(r"[^a-z0-9]+", "", lowered)


def merge_unique_skills(existing_skills_text: str, new_keywords: Iterable[str]) -> list[str]:
    """Merge existing and new skills while preserving order and removing overlaps."""
    merged: list[str] = []
    seen: set[str] = set()

    for skill in split_skills(existing_skills_text):
        key = _normalize_skill_key(skill)
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(skill)

    for keyword in new_keywords:
        skill = str(keyword or "").strip()
        if not skill:
            continue
        key = _normalize_skill_key(skill)
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(skill)

    return merged


def join_skills_csv(skills: Iterable[str]) -> str:
    """Render skill entries as one comma-separated line."""
    return ", ".join([str(skill).strip() for skill in skills if str(skill).strip()])
